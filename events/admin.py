# Register your models here.
from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'creator', 'scheduled_date', 'is_featured')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informació bàsica', {
            'fields': ('title', 'description', 'creator', 'category')
        }),
        ('Programació', {
            'fields': ('scheduled_date', 'status', 'max_viewers')
        }),
        ('Multimèdia', {
            'fields': ('thumbnail', 'stream_url', 'tags')
        }),
        ('Configuració', {
            'fields': ('is_featured', 'created_at', 'updated_at')
        }),
    )