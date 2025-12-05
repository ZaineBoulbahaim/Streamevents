# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
import re
from PIL import Image
import os
from django.core.files.base import ContentFile
from io import BytesIO

User = get_user_model()

class Event(models.Model):
    # Choices para categorías
    CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('music', 'Música'),
        ('talk', 'Xerrades'),
        ('education', 'Educació'),
        ('sports', 'Esports'),
        ('entertainment', 'Entreteniment'),
        ('technology', 'Tecnologia'),
        ('art', 'Art i Creativitat'),
        ('other', 'Altres'),
    ]
    
    # Choices para estados
    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]
    
    # Campos del modelo
    title = models.CharField(
        max_length=200,
        verbose_name='Títol'
    )
    
    description = models.TextField(
        verbose_name='Descripció'
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events_created',
        verbose_name='Creador'
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Categoria'
    )
    
    scheduled_date = models.DateTimeField(
        verbose_name='Data i hora programada'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Estat'
    )
    
    thumbnail = models.ImageField(
        upload_to='events/thumbnails/',
        null=True,
        blank=True,
        verbose_name='Imatge de portada'
    )
    
    max_viewers = models.PositiveIntegerField(
        default=100,
        verbose_name='Màxim espectadors'
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacat'
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Etiquetes'
    )
    
    stream_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='URL del streaming'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de creació'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualització'
    )
    class Meta:
        ordering = ['-created_at']  # Ordena eventos por fecha de creación descendente
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'

    def __str__(self):
        return self.title  # Muestra el título como representación del objeto

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})  # URL al detalle del evento

    # Propiedades para comprobar estado
    @property
    def is_live(self):
        return self.status == 'live'  # True si está en directo

    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date > timezone.now()  # True si aún no ha comenzado

    # Duración estimada según categoría
    def get_duration(self):
        category_durations = {
            'gaming': 180, 'music': 90, 'talk': 60, 'education': 120, 'sports': 150,
            'entertainment': 120, 'technology': 90, 'art': 120, 'other': 90,
        }
        return category_durations.get(self.category, 90)  # Duración por defecto 1.5h

    # Convierte etiquetas a lista
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    # Placeholder para futuras funciones de streaming
    def get_stream_embed_url(self):
        return None

    # Obtener miniatura de YouTube desde URL
    def get_youtube_thumbnail(self):
        if not self.stream_url:
            return None
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
        ]
        for pattern in youtube_patterns:
            match = re.search(pattern, self.stream_url)
            if match:
                video_id = match.group(1)
                return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        return None

    # Obtener ID de YouTube
    def get_youtube_id(self):
        if not self.stream_url:
            return None
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
        ]
        for pattern in youtube_patterns:
            match = re.search(pattern, self.stream_url)
            if match:
                return match.group(1)
        return None

    # Actualiza estado según fecha y duración
    def update_status_based_on_time(self):
        now = timezone.now()
        if self.status == 'scheduled' and self.scheduled_date <= now:
            self.status = 'live'
            self.save(update_fields=['status', 'updated_at'])
            return True
        elif self.status == 'live':
            duration_minutes = self.get_duration()
            end_time = self.scheduled_date + timezone.timedelta(minutes=duration_minutes)
            if now >= end_time:
                self.status = 'finished'
                self.save(update_fields=['status', 'updated_at'])
                return True
        return False

    # Thumbnail por defecto según categoría
    def get_default_thumbnail(self):
        category_defaults = {
            'gaming': 'default/gaming.jpg', 'music': 'default/music.jpg', 'talk': 'default/talk.jpg',
            'education': 'default/education.jpg', 'sports': 'default/sports.jpg',
            'entertainment': 'default/entertainment.jpg', 'technology': 'default/technology.jpg',
            'art': 'default/art.jpg', 'other': 'default/other.jpg',
        }
        return category_defaults.get(self.category, 'default/other.jpg')

    # Guardado y redimensionado automático de thumbnail
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.thumbnail and hasattr(self.thumbnail, 'path'):
            try:
                self._resize_thumbnail()
            except Exception as e:
                pass  # Si falla, se ignora

    # Redimensiona la thumbnail
    def _resize_thumbnail(self):
        img = Image.open(self.thumbnail.path)
        max_size = (800, 450)  # Tamaño máximo
        if img.height > max_size[1] or img.width > max_size[0]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            thumb_io = BytesIO()
            if img.format and img.format.upper() in ['JPEG', 'JPG']:
                img.save(thumb_io, format='JPEG', quality=85)
                file_extension = 'jpg'
            elif img.format and img.format.upper() == 'PNG':
                img.save(thumb_io, format='PNG')
                file_extension = 'png'
            else:
                img.save(thumb_io, format='JPEG', quality=85)
                file_extension = 'jpg'
            name = os.path.splitext(self.thumbnail.name)[0]
            new_name = f"{name}_resized.{file_extension}"
            self.thumbnail.save(new_name, ContentFile(thumb_io.getvalue()), save=False)
            # Actualiza la base de datos directamente para evitar recursión
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("UPDATE events_event SET thumbnail = %s WHERE id = %s",
                               [self.thumbnail.name, self.id])