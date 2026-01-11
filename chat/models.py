from django.db import models
from django.conf import settings
from django.utils.timesince import timesince

# Create your models here.
class ChatMessage(models.Model):
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField(
        max_length=500
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    is_deleted = models.BooleanField(
        default=False
    )
    is_highlighted = models.BooleanField(
        default=False
    )
    def __str__(self):
        """
        Representación del objeto
        """
        return f"{self.user.username}: {self.message[:50]}"
    
    def can_delete(self, user):
        """
        Metodo para comprobar si el usuario puede borrar el mensaje
        """
        if not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        if user == self.user:
            return True

        if user == self.event.creator:
            return True

        return False
    
    def get_user_display_name(self):
        """
        Obtenir el nom de l'usuari
        """
        return getattr(self.user, 'display_name', None) or self.user.username
    
    def get_time_since(self):
        """
        Obtenir el temps que ha passat
        """
        return f"fa {timesince(self.created_at)}"


class Meta:
    ordering = ['created_at']
    verbose_name = 'Missatge de Xat'
    verbose_name_plural = 'Missatges de Xat'
