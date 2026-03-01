from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k


def build_event_text(event: Event) -> str:
    """
    Construye un texto representativo del evento concatenando sus campos principales.
    Este texto es el que se usaría si quisiéramos re-embedar eventos,
    pero en el retriever lo usamos como referencia de qué datos tiene el evento.
    """
    return " | ".join([
        (event.title or "").strip(),
        (event.description or "").strip(),
        (event.category or "").strip(),
        (event.tags or "").strip(),
    ]).strip()


def retrieve_events(query: str, only_future: bool = True, k: int = 8):
    """
    Dado un texto de consulta del usuario, busca los eventos más relevantes.
    
    Proceso:
    1. Convierte la consulta del usuario a un vector (embedding)
    2. Busca primero entre eventos futuros
    3. Si no encuentra nada, amplía la búsqueda a todos los eventos
    4. Descarta eventos con score bajo (menos de 0.25)
    5. Retorna los K más similares
    """

    # Paso 1: Convertir la consulta a vector
    query_vector = embed_text(query)

    def search_in_queryset(queryset):
        """Función auxiliar que busca en un queryset dado."""
        items = []
        for event in queryset.only("id", "title", "scheduled_date", "category", "tags", "embedding"):
            event_embedding = getattr(event, "embedding", None)
            # Solo incluimos eventos que tengan embedding válido
            if isinstance(event_embedding, list) and len(event_embedding) > 0:
                items.append((event, event_embedding))

        # Calculamos cosine similarity y obtenemos los más relevantes
        ranked_events = cosine_top_k(query_vector, items, k=max(k, 20))

        # Filtramos por score mínimo
        ranked_events = [(event, similitud) for (event, similitud) in ranked_events if similitud >= 0.25]

        return ranked_events[:k]

    # Paso 2: Buscar primero en eventos futuros si only_future=True
    if only_future:
        future_queryset = Event.objects.filter(scheduled_date__gte=timezone.now())
        resultado = search_in_queryset(future_queryset)

        # Paso 3: Si no hay resultados futuros, ampliar a todos los eventos
        if not resultado:
            all_queryset = Event.objects.all()
            resultado = search_in_queryset(all_queryset)
    else:
        # Si only_future=False, buscar directamente en todos
        resultado = search_in_queryset(Event.objects.all())

    return resultado[:3]