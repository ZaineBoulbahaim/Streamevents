# Create your views here.
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from events.models import Event
from .models import ChatMessage
from .forms import ChatMessageForm



@login_required
@require_POST
def chat_send_message(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if event.status != 'live':
        return JsonResponse(
            {'success': False, 'error': 'L\'esdeveniment no està en directe.'},
            status=400
        )

    form = ChatMessageForm(request.POST)

    if form.is_valid():
        message = form.save(commit=False)
        message.user = request.user
        message.event = event
        message.save()

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'user': message.user.username,
                'display_name': message.get_user_display_name(),
                'message': message.message,
                'created_at': message.get_time_since(),
                'can_delete': message.can_delete(request.user),
                'is_highlighted': message.is_highlighted,
            }
        })

    return JsonResponse(
        {'success': False, 'errors': form.errors},
        status=400
    )

def chat_load_messages(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    all_messages = ChatMessage.objects.filter(event=event).order_by('created_at')[:50]

    messages_list = []

    for msg in all_messages:
        if msg.is_deleted:  # filtrar en Python
            continue

        messages_list.append({
            'id': msg.id,
            'user': msg.user.username,
            'display_name': msg.get_user_display_name(),
            'message': msg.message,
            'created_at': msg.get_time_since(),
            'can_delete': msg.can_delete(request.user) if request.user.is_authenticated else False,
            'is_highlighted': msg.is_highlighted,
        })

    return JsonResponse({'messages': messages_list})

@login_required
@require_POST
def chat_delete_message(request, message_pk):
    message = get_object_or_404(ChatMessage, pk=message_pk)

    if not message.can_delete(request.user):
        return JsonResponse({'success': False, 'error': 'No tens permisos per eliminar aquest missatge.'}, status=403)

    message.is_deleted = True
    message.save()

    return JsonResponse({'success': True})

@login_required
@require_POST
def chat_toggle_highlight(request, message_pk):
    message = get_object_or_404(ChatMessage, pk=message_pk)
    event = message.event

    if request.user != event.creator:
        return JsonResponse(
            {
                'success': False,
                'error': 'No tens permisos per destacar aquest missatge.'
            },
            status=403
        )

    message.is_highlighted = not message.is_highlighted
    message.save()

    return JsonResponse({
        'success': True,
        'is_highlighted': message.is_highlighted
    })
