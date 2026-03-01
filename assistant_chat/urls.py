from django.urls import path
from .views import chat_page, chat_api, chat_stream_api

# Nombre del espacio de la app para usar en templates con {% url %}
app_name = "assistant_chat"

urlpatterns = [
    # Página principal del chat (GET) -> renderiza el HTML
    path("assistant/", chat_page, name="page"),

    # Endpoint sin stream (POST) -> devuelve JSON completo de una vez
    path("assistant/api/chat/", chat_api, name="api_chat"),

    # Endpoint con stream (POST) -> devuelve tokens uno a uno via SSE
    path("assistant/api/stream/", chat_stream_api, name="api_stream"),
]