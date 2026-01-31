"""
Esta vista maneja las peticiones de búsqueda en lenguaje natural.
"""
import logging
from django.shortcuts import render
from django.utils import timezone
from events.models import Event
from .services.embeddings import embed_text, model_name
from .services.ranker import cosine_top_k

# Configurar logger para esta vista
logger = logging.getLogger(__name__)

def _event_text(e: Event) -> str:
    """
    Combina los campos relevantes de un evento en un solo texto.
    
    Args:
        e: Objeto Event
        
    Returns:
        str: Texto combinado separado por " | "
    """
    parts = [
        e.title or "",
        e.description or "",
        e.category or "",
        e.tags or "",
    ]
    return " | ".join([p.strip() for p in parts if p and p.strip()])


def semantic_search(request):
    """
    Vista principal de búsqueda semántica.
    
    URL: /semantic/
    Método: GET
    
    Parámetros GET:
        - q: Query de búsqueda (texto libre)
        - future: "1" para filtrar solo eventos futuros
        
    Returns:
        HttpResponse: Template renderizado con resultados
    """
    
    # Umbral mínimo de similitud para mostrar resultados
    MIN_SCORE_THRESHOLD = 0.3
    
    #  1. OBTENER PARÁMETROS 
    
    q = (request.GET.get("q") or "").strip()
    future_param = request.GET.get("future")
    
    # Lógica del checkbox de eventos futuros
    if future_param is None:
        only_future = True  # Por defecto, solo futuros
    else:
        only_future = (future_param == "1")
    
    logger.info(
        f"Búsqueda semántica: query='{q}', only_future={only_future}"
    )
    
    results = []
    
    #  2. PROCESAR BÚSQUEDA 
    
    if not q:
        # No hay búsqueda, devolver formulario vacío
        logger.debug("No se proporcionó query, mostrando formulario vacío")
        context = {
            "query": q,
            "results": results,
            "only_future": only_future,
            "embedding_model": model_name(),
        }
        return render(request, "semantic_search/search.html", context)
    
    # Generar embedding de la búsqueda
    q_vec = embed_text(q)
    logger.debug(f"Embedding de query generado: {len(q_vec)} dimensiones")
    
    #  3. OBTENER EVENTOS CANDIDATOS 
    
    qs = Event.objects.all()
    
    if only_future:
        qs = qs.filter(scheduled_date__gte=timezone.now())
    
    logger.debug(
        f"Eventos candidatos: {qs.count()} "
        f"({'futuros' if only_future else 'todos'})"
    )
    
    #  4. PREPARAR ITEMS PARA RANKING 
    
    items = []
    eventos_sin_embedding = 0
    
    for e in qs:
        embedding = getattr(e, "embedding", None)
        
        # Validar que el embedding existe y es válido
        if embedding and isinstance(embedding, list) and len(embedding) > 0:
            items.append((e, embedding))
        else:
            eventos_sin_embedding += 1
    
    if eventos_sin_embedding > 0:
        logger.warning(
            f"{eventos_sin_embedding} evento(s) sin embedding válido "
            f"(ejecuta: python manage.py backfill_event_embeddings)"
        )
    
    if len(items) == 0:
        logger.warning("No hay eventos con embeddings para comparar")
        context = {
            "query": q,
            "results": results,
            "only_future": only_future,
            "embedding_model": model_name(),
        }
        return render(request, "semantic_search/search.html", context)
    
    logger.debug(f"Items válidos para ranking: {len(items)}")
    
    #  5. CALCULAR SIMILITUDES 
    
    ranked = cosine_top_k(q_vec, items, k=20)
    
    # Logging detallado de scores (solo en modo DEBUG)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Top 10 resultados (antes de filtrar):")
        for i, (event, score) in enumerate(ranked[:10], 1):
            logger.debug(f"  {i:2}. [{score:.4f}] {event.title[:50]}")
    
    #  6. FILTRAR POR SCORE MÍNIMO 
    
    filtered_results = [
        (event, score) 
        for event, score in ranked 
        if score >= MIN_SCORE_THRESHOLD
    ]
    
    results = filtered_results
    
    logger.info(
        f"Resultados: {len(results)}/{len(ranked)} "
        f"(threshold >= {MIN_SCORE_THRESHOLD})"
    )
    
    #  7. PREPARAR CONTEXTO Y RENDERIZAR 
    
    context = {
        "query": q,
        "results": results,
        "only_future": only_future,
        "embedding_model": model_name(),
    }
    
    return render(request, "semantic_search/search.html", context)