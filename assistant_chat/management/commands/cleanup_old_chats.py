from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from assistant_chat.models import ChatSession


class Command(BaseCommand):
    """
    Comando personalizado de Django para eliminar sesiones de chat antiguas.

    Se ejecuta con:
        python manage.py cleanup_old_chats

    En producción se programaría con cron (Linux) o Task Scheduler (Windows)
    para ejecutarse automáticamente cada día.
    """

    # Descripción que aparece al ejecutar: python manage.py help cleanup_old_chats
    help = "Elimina les sessions de xat amb més de 15 dies d'inactivitat"

    def handle(self, *args, **options):
        """
        Método principal que se ejecuta cuando llamamos al comando.
        Django llama a este método automáticamente.
        """

        # Calculamos la fecha límite: hoy menos 15 días
        # Las sesiones con last_activity anterior a esta fecha serán eliminadas
        expiration_date = timezone.now() - timedelta(days=15)

        # Buscamos todas las sesiones con última actividad anterior a la fecha límite
        # Gracias al CASCADE de ChatMessage, al borrar la sesión
        # se borran también todos sus mensajes automáticamente
        old_sessions = ChatSession.objects.filter(last_activity__lt=expiration_date)

        # Guardamos el número de sesiones antes de borrar para el informe
        total_deleted = old_sessions.count()

        # Eliminamos todas las sesiones antiguas de una sola consulta a la BD
        old_sessions.delete()

        # Mostramos un mensaje de confirmación en la terminal
        # self.stdout.write es la forma correcta de imprimir en comandos Django
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Eliminades {total_deleted} sessions de xat antigues."
            )
        )