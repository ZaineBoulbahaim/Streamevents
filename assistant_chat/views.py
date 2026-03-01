import json
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import ChatSession, ChatMessage
from .services.retriever import retrieve_events
from .services.prompts import build_prompt
from .services.llm_ollama import generate, generate_stream


def chat_page(request):
    """
    Vista que renderiza la página HTML del chat.
    Si el usuario está autenticado, carga su historial de mensajes.
    """

    history = []

    if request.user.is_authenticated:
        # Buscamos la sesión más reciente del usuario
        session = ChatSession.objects.filter(user=request.user).first()

        if session:
            # Obtenemos todos los mensajes ordenados por timestamp
            history = list(session.messages.values("role", "text", "timestamp"))

    return render(request, "assistant_chat/chat.html", {"history": history})


@csrf_exempt
def chat_api(request):
    """
    Endpoint principal del chat. Acepta peticiones POST con JSON.
    Versión sin stream: devuelve la respuesta completa de una vez.

    Request body: {"message": "vull un concert de jazz", "only_future": true}
    Response JSON: {"answer": "...", "follow_up": "...", "events": [...]}
    """

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Paso 1: Recuperar eventos relevantes usando búsqueda semántica
    ranked_events = retrieve_events(user_message, only_future=only_future, k=8)

    # Paso 2: Preparar los eventos como diccionarios para el contexto del LLM
    candidates = []
    for event, score in ranked_events:
        candidates.append({
            "id": int(event.pk),
            "title": event.title,
            "scheduled_date": event.scheduled_date.isoformat() if event.scheduled_date else None,
            "category": event.category,
            "tags": event.tags or "",
            "url": event.get_absolute_url(),
            "score": round(float(score), 3),
        })

    # Paso 3: Construir el prompt con los eventos como contexto
    prompt = build_prompt(user_message, candidates)

    # Paso 4: Llamar al LLM y obtener su respuesta en texto
    llm_text = generate(prompt)

    # Paso 5: Intentar parsear la respuesta del LLM como JSON
    try:
        llm_json = json.loads(llm_text)
    except Exception:
        llm_json = {
            "answer": "No he pogut generar una resposta estructurada. Prova amb una consulta més concreta.",
            "recommended_ids": [candidate["id"] for candidate in candidates[:3]],
            "follow_up": ""
        }

    # Paso 6: Filtrar recommended_ids para que solo sean de los candidatos
    allowed_ids = {candidate["id"] for candidate in candidates}
    recommended_ids = [
        event_id for event_id in llm_json.get("recommended_ids", [])
        if event_id in allowed_ids
    ]

    # Paso 7: Preparar las cards finales
    event_cards = [candidate for candidate in candidates if candidate["id"] in recommended_ids]

    if not event_cards:
        event_cards = candidates[:3]

    # Paso 8: Guardar historial en BD solo si el usuario está autenticado
    if request.user.is_authenticated:
        session, created = ChatSession.objects.get_or_create(user=request.user)

        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.ROLE_USER,
            text=user_message,
        )

        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.ROLE_ASSISTANT,
            text=llm_json.get("answer", ""),
        )

        session.last_activity = timezone.now()
        session.save()

    return JsonResponse({
        "answer": llm_json.get("answer", ""),
        "follow_up": llm_json.get("follow_up", ""),
        "events": event_cards,
    })


@csrf_exempt
def chat_stream_api(request):
    """
    Endpoint de streaming con Server-Sent Events (SSE).
    A diferencia de chat_api, este endpoint envía tokens uno a uno
    en tiempo real mientras el modelo los genera.

    También hace el retrieval de eventos y los devuelve al final
    como un evento SSE especial con formato JSON.

    Request body: {"message": "...", "only_future": true}
    Response: stream de eventos SSE
    """

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Retrieval de eventos (igual que en chat_api)
    ranked_events = retrieve_events(user_message, only_future=only_future, k=8)

    candidates = []
    for event, score in ranked_events:
        candidates.append({
            "id": int(event.pk),
            "title": event.title,
            "scheduled_date": event.scheduled_date.isoformat() if event.scheduled_date else None,
            "category": event.category,
            "tags": event.tags or "",
            "url": event.get_absolute_url(),
            "score": round(float(score), 3),
        })

    prompt = build_prompt(user_message, candidates)

    def event_stream():
        """
        Generador que produce eventos SSE.
        Formato obligatorio SSE: cada mensaje empieza con 'data: ' y acaba con '\n\n'
        """

        # Acumulamos el texto completo para guardarlo en BD al final
        full_response = ""

        # Enviamos cada token del modelo como un evento SSE
        for token in generate_stream(prompt):
            full_response += token
            # Escapamos saltos de línea para no romper el formato SSE
            safe_token = token.replace("\n", "\\n")
            yield f"data: {safe_token}\n\n"

        # Guardamos el historial en BD si el usuario está autenticado
        # Nota: en SSE no tenemos acceso directo a request.user dentro del generador
        # por eso guardamos el user_id antes de entrar al generador
        if user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(pk=user_id)
                session, created = ChatSession.objects.get_or_create(user=user)
                ChatMessage.objects.create(
                    session=session,
                    role=ChatMessage.ROLE_USER,
                    text=user_message,
                )
                ChatMessage.objects.create(
                    session=session,
                    role=ChatMessage.ROLE_ASSISTANT,
                    text=full_response,
                )
                session.last_activity = timezone.now()
                session.save()
            except Exception:
                pass

        # Evento especial con los eventos candidatos para las cards
        # El frontend lo detecta por el prefijo "EVENTS:"
        events_data = json.dumps(candidates, ensure_ascii=False)
        yield f"data: EVENTS:{events_data}\n\n"

        # Evento final para indicar al frontend que el stream ha acabado
        yield "data: [DONE]\n\n"

    # Guardamos el user_id antes de entrar al generador
    # porque dentro del generador no podemos acceder a request.user de forma segura
    user_id = request.user.pk if request.user.is_authenticated else None

    # StreamingHttpResponse envía la respuesta chunk a chunk
    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream"   # Tipo MIME obligatorio para SSE
    )

    # Cabeceras necesarias para SSE
    response["Cache-Control"] = "no-cache"      # No cachear la respuesta
    response["X-Accel-Buffering"] = "no"        # Desactivar buffering en nginx

    return response