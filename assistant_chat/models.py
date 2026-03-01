# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatSession(models.Model):
    """
    Representa una sesión de conversación de un usuario autenticado.
    Cada usuario puede tener múltiples sesiones (una por conversación).
    """

    # Usuario propietario de la sesión
    # settings.AUTH_USER_MODEL es la forma correcta de referenciar
    # el modelo de usuario personalizado (CustomUser)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Si se borra el usuario, se borran sus sesiones
        related_name="chat_sessions"
    )

    # Fecha de creación de la sesión
    created_at = models.DateTimeField(auto_now_add=True)

    # Fecha de última actividad (se actualiza cada vez que hay un mensaje)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        # Ordenar por última actividad, más reciente primero
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Sessió de {self.user} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def is_expired(self) -> bool:
        """
        Comprueba si la sesión tiene más de 15 días de antigüedad.
        Retorna True si debe ser eliminada.
        """
        expiration_days = 15
        # Calculamos la diferencia entre ahora y la última actividad
        days_inactive = (timezone.now() - self.last_activity).days
        return days_inactive >= expiration_days


class ChatMessage(models.Model):
    """
    Representa un mensaje individual dentro de una sesión de chat.
    Puede ser del usuario (role='user') o del asistente (role='assistant').
    """

    # Roles posibles para el mensaje
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES = [
        (ROLE_USER, "Usuari"),
        (ROLE_ASSISTANT, "Assistent"),
    ]

    # Sesión a la que pertenece este mensaje
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,  # Si se borra la sesión, se borran sus mensajes
        related_name="messages"
    )

    # Quién envió el mensaje: 'user' o 'assistant'
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Contenido del mensaje
    text = models.TextField()

    # Fecha y hora del mensaje (se asigna automáticamente al crear)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordenar por timestamp, más antiguo primero (orden natural de conversación)
        ordering = ["timestamp"]

    def __str__(self):
        return f"[{self.role}] {self.text[:50]}..."