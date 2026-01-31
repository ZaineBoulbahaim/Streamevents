"""
Comando: backfill_event_embeddings
Genera embeddings semánticos para eventos que no los tienen.

Este comando procesa eventos de la base de datos, genera sus representaciones
vectoriales (embeddings) usando un modelo de IA, y las guarda para permitir
búsquedas semánticas.
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text, model_name

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Comando para generar embeddings de eventos existentes.
    
    Hereda de BaseCommand para crear un comando personalizado de Django
    que puede ejecutarse desde manage.py.
    """
    
    help = "Genera i desa embeddings per a Events que no en tinguin (o tots amb --force)"

    def add_arguments(self, parser):
        """
        Define argumentos opcionales de línea de comandos.
        
        Args:
            parser: ArgumentParser para añadir opciones
        """
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recalcula embeddings encara que ja existeixin"
        )
        
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limita el nombre d'events a processar (0 = tots)"
        )

    def handle(self, *args, **options):
        """
        Lógica principal del comando.
        
        Proceso:
        1. Lee opciones de línea de comandos
        2. Construye queryset de eventos a procesar
        3. Para cada evento: genera embedding y lo guarda
        4. Muestra resumen de operación
        
        Args:
            options: Diccionario con argumentos del comando
        """
        
        force = options["force"]
        limit = options["limit"]
        
        # Construir queryset de eventos a procesar
        qs = Event.objects.all().order_by("created_at")
        
        if not force:
            qs = qs.filter(embedding__isnull=True)
        
        if limit and limit > 0:
            qs = qs[:limit]
        
        total_candidatos = qs.count()
        
        # Validar que hay eventos para procesar
        if total_candidatos == 0:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  No hi ha events per processar. "
                    "Tots ja tenen embedding o la BD està buida."
                )
            )
            return
        
        # Informar inicio de proceso
        self.stdout.write(
            self.style.SUCCESS(f"🚀 Processant {total_candidatos} event(s)...\n")
        )
        
        if force:
            self.stdout.write("   ℹ️  Mode --force: recalculant tots els embeddings")
        if limit > 0:
            self.stdout.write(f"   ℹ️  Límit: {limit} events màxim")
        
        self.stdout.write("")
        
        # Procesar cada evento
        total_procesados = 0
        total_omitidos = 0
        
        for idx, evento in enumerate(qs, start=1):
            # Combinar campos relevantes del evento
            text = " | ".join([
                (evento.title or "").strip(),
                (evento.description or "").strip(),
                (evento.category or "").strip(),
                (evento.tags or "").strip(),
            ]).strip()
            
            # Validar que el evento tiene contenido
            if not text:
                logger.warning(f"Evento #{evento.id} omitido: sin contenido")
                total_omitidos += 1
                continue
            
            self.stdout.write(
                f"   [{idx}/{total_candidatos}] 🔄 {evento.title[:50]}..."
            )
            
            try:
                # Generar embedding vectorial
                vec = embed_text(text)
                
                if not vec or len(vec) == 0:
                    logger.error(f"Error generando embedding para evento #{evento.id}")
                    continue
                
                # Guardar en base de datos
                evento.embedding = vec
                evento.embedding_model = model_name()
                evento.embedding_updated_at = timezone.now()
                
                evento.save(update_fields=[
                    "embedding",
                    "embedding_model",
                    "embedding_updated_at"
                ])
                
                total_procesados += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Guardat: {len(vec)} dimensions")
                )
                
            except Exception as ex:
                logger.error(f"Error procesando evento #{evento.id}: {str(ex)}")
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Error: {str(ex)}")
                )
                continue
        
        # Mostrar resumen final
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Procés completat!\n"
                f"   • Events processats: {total_procesados}\n"
                f"   • Events omesos: {total_omitidos}\n"
                f"   • Model utilitzat: {model_name()}"
            )
        )
        
        if total_omitidos > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  {total_omitidos} event(s) sense contingut vàlid"
                )
            )