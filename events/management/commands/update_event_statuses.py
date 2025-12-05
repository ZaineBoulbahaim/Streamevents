from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
import logging

# Configuramos el logger para registrar información y errores
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    # Descripción del comando que aparece en la consola
    help = 'Actualitza automàticament els estats dels esdeveniments basant-se en la data i hora'
    
    def handle(self, *args, **options):
        # Mensaje inicial indicando que el proceso comienza
        self.stdout.write('🚀 Iniciant actualització automàtica d\'estats...')
        
        # Seleccionamos solo los eventos que pueden necesitar un cambio de estado
        # 'scheduled' → puede pasar a 'live'
        # 'live' → puede pasar a 'finished'
        events_to_check = Event.objects.filter(
            status__in=['scheduled', 'live']
        )
        
        updated_count = 0  # Contador de eventos actualizados
        
        # Recorremos los eventos encontrados
        for event in events_to_check:
            try:
                # Llamamos al método del modelo que decide si actualizar o no el estado
                if event.update_status_based_on_time():
                    updated_count += 1  # Sumamos si hubo cambio
                    self.stdout.write(
                        self.style.SUCCESS(
                            # Mostramos el título del evento y su nuevo estado legible
                            f'✓ Actualitzat: {event.title} -> {event.get_status_display()}'
                        )
                    )
            except Exception as e:
                # Si ocurre un error con algún evento, lo mostramos en consola
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error actualitzant {event.title}: {str(e)}'
                    )
                )
        
        # Mensaje final indicando cuántos eventos fueron actualizados
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Actualització completada. {updated_count} esdeveniments actualitzats.'
            )
        )
