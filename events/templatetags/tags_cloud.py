from django import template
from django.db.models import Count
from events.models import Event
import math

register = template.Library()

@register.inclusion_tag('events/includes/tags_cloud.html')
def tags_cloud(min_count=1, limit=20):
    """Genera una nube de etiquetas"""
    events = Event.objects.exclude(tags='')
    tag_counts = {}
    
    for event in events:
        if event.tags:
            tags = [tag.strip().lower() for tag in event.tags.split(',') if tag.strip()]
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Filtrar por mínimo de apariciones
    filtered_tags = {k: v for k, v in tag_counts.items() if v >= min_count}
    
    # Ordenar por frecuencia y limitar
    sorted_tags = sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    # Calcular tamaños para la nube (clases CSS)
    if sorted_tags:
        min_freq = min(count for _, count in sorted_tags)
        max_freq = max(count for _, count in sorted_tags)
        
        tags_with_size = []
        for tag, count in sorted_tags:
            if max_freq > min_freq:
                # Determinar clase CSS basada en frecuencia
                ratio = (count - min_freq) / (max_freq - min_freq)
                if ratio < 0.3:
                    size_class = 'tag-xs'
                elif ratio < 0.6:
                    size_class = 'tag-sm'
                else:
                    size_class = 'tag-lg'
            else:
                size_class = 'tag-sm'
            
            tags_with_size.append({
                'name': tag,
                'count': count,
                'size_class': size_class
            })
    else:
        tags_with_size = []
    
    return {'tags': tags_with_size}