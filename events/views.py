from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm
import traceback
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Count

def event_list_view(request):
    """
    Vista de llistat d'esdeveniments amb cerca i filtres
    """
    try:
        # Obtenir tots els esdeveniments (sin select_related para MongoDB)
        events_list = Event.objects.all()
        
        # Inicialitzar formulari de cerca
        search_form = EventSearchForm(request.GET or None)
        events_filtered = events_list
        
        # Aplicar filtres si el formulari és vàlid
        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search')
            category = search_form.cleaned_data.get('category')
            status = search_form.cleaned_data.get('status')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            
            # Filtrar per cerca de text
            if search_query:
                events_filtered = events_filtered.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(tags__icontains=search_query)
                )
            
            # Filtrar per categoria
            if category:
                events_filtered = events_filtered.filter(category=category)
            
            # Filtrar per estat
            if status:
                events_filtered = events_filtered.filter(status=status)
            
            # Filtrar per data (VERSIÓN PARA MONGODB)
            if date_from:
                # Crear datetime desde la fecha (inicio del día)
                start_datetime = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
                events_filtered = events_filtered.filter(scheduled_date__gte=start_datetime)
            
            if date_to:
                # Crear datetime hasta la fecha (fin del día)
                end_datetime = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
                events_filtered = events_filtered.filter(scheduled_date__lte=end_datetime)
        
        # Ordenar per data de creació (més recents primer)
        events_filtered = events_filtered.order_by('-created_at')
        
        # Obtenir esdeveniments destacados - VERSIÓN SEGURA
        # Primero obtenemos todos y filtramos manualmente
        all_events_list = list(events_filtered)
        featured_events = [event for event in all_events_list if event.is_featured][:3]
        
        # Paginació (9 per pàgina)
        paginator = Paginator(events_filtered, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_form': search_form,
            'featured_events': featured_events,
            'total_events': events_list.count(),
            'now': timezone.now(),
        }
        
        return render(request, 'events/event_list.html', context)
        
    except Exception as e:
        print("ERROR en event_list_view:", str(e))
        traceback.print_exc()
        
        # Versión de emergencia sin filtros
        events_list = Event.objects.all().order_by('-created_at')
        paginator = Paginator(events_list, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'total_events': events_list.count(),
            'now': timezone.now(),
            'error': str(e),
        }
        
        return render(request, 'events/event_list.html', context)

def event_detail_view(request, pk):
    """
    Vista de detall d'esdeveniment
    """
    # Sin select_related para MongoDB
    event = get_object_or_404(Event, pk=pk)
    
    # Verificar si l'usuari és el creador
    is_creator = request.user.is_authenticated and request.user == event.creator
    
    # Generar URL embed per al streaming
    embed_url = event.get_stream_embed_url()
    
    context = {
        'event': event,
        'is_creator': is_creator,
        'embed_url': embed_url,
        'now': timezone.now(),
    }
    
    return render(request, 'events/event_detail.html', context)

@login_required
def event_create_view(request):
    """
    Vista de creació d'esdeveniment
    """
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            
            messages.success(request, 'Esdeveniment creat amb èxit!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventCreationForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Crear nou esdeveniment',
    }
    
    return render(request, 'events/event_form.html', context)

@login_required
def event_update_view(request, pk):
    """
    Vista d'edició d'esdeveniment
    """
    event = get_object_or_404(Event, pk=pk)
    
    # Verificar permisos: només el creador pot editar
    if request.user != event.creator:
        messages.error(request, 'No tens permís per editar aquest esdeveniment.')
        return redirect('events:event_detail', pk=event.pk)
    
    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event, 
                               user=request.user, event=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Esdeveniment actualitzat amb èxit!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventUpdateForm(instance=event, user=request.user, event=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Editar: {event.title}',
    }
    
    return render(request, 'events/event_form.html', context)

@login_required
def event_delete_view(request, pk):
    """
    Vista d'eliminació d'esdeveniment
    """
    event = get_object_or_404(Event, pk=pk)
    
    # Verificar permisos: només el creador pot eliminar
    if request.user != event.creator:
        messages.error(request, 'No tens permís per eliminar aquest esdeveniment.')
        return redirect('events:event_detail', pk=event.pk)
    
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Esdeveniment "{event_title}" eliminat amb èxit.')
        return redirect('events:event_list')
    
    context = {
        'event': event,
    }
    
    return render(request, 'events/event_confirm_delete.html', context)

@login_required
def my_events_view(request):
    """
    Vista d'esdeveniments de l'usuari
    """
    # Obtenir esdeveniments creats per l'usuari actual
    events_list = Event.objects.filter(creator=request.user).order_by('-created_at')
    
    # Filtrar per estat si s'ha especificat
    status_filter = request.GET.get('status', '')
    if status_filter:
        events_list = events_list.filter(status=status_filter)
    
    # Estadístiques bàsiques
    total_events = events_list.count()
    live_events = events_list.filter(status='live').count()
    scheduled_events = events_list.filter(status='scheduled').count()
    finished_events = events_list.filter(status='finished').count()
    
    # Paginació
    paginator = Paginator(events_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_events': total_events,
        'live_events': live_events,
        'scheduled_events': scheduled_events,
        'finished_events': finished_events,
        'current_status_filter': status_filter,
        'now': timezone.now(),
    }
    
    return render(request, 'events/my_events.html', context)

def events_by_category_view(request, category):
    """
    Vista d'esdeveniments per categoria
    """
    # Validar que la categoria existeix
    valid_categories = [choice[0] for choice in Event.CATEGORY_CHOICES]
    
    if category not in valid_categories:
        messages.error(request, 'Categoria no vàlida.')
        return redirect('events:event_list')
    
    # Obtenir esdeveniments de la categoria
    events_list = Event.objects.filter(category=category).order_by('-created_at')
    
    # Obtenir el nom amigable de la categoria
    category_name = dict(Event.CATEGORY_CHOICES).get(category, category)
    
    # Paginació
    paginator = Paginator(events_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'category_name': category_name,
        'total_events': events_list.count(),
        'now': timezone.now(),
    }
    
    return render(request, 'events/events_by_category.html', context)

def get_tags_autocomplete(request):
    """
    API para autocompletar etiquetas
    """
    query = request.GET.get('q', '')
    
    if query:
        # Buscar etiquetas que contengan la query
        events = Event.objects.filter(tags__icontains=query)
        all_tags = []
        
        for event in events:
            if event.tags:
                tags = [tag.strip().lower() for tag in event.tags.split(',') if tag.strip()]
                all_tags.extend(tags)
        
        # Filtrar tags que contengan la query y eliminar duplicados
        matching_tags = sorted(list(set(
            tag for tag in all_tags if query.lower() in tag
        )))[:10]  # Limitar a 10 resultados
    else:
        # Si no hay query, devolver tags más populares
        events = Event.objects.exclude(tags='')
        tag_counts = {}
        
        for event in events:
            if event.tags:
                tags = [tag.strip().lower() for tag in event.tags.split(',') if tag.strip()]
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        matching_tags = sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:10]
    
    return JsonResponse({'tags': matching_tags})