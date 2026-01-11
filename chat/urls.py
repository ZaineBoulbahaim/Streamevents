from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('load/<int:event_pk>/', views.chat_load_messages, name='load_messages'),
    path('send/<int:event_pk>/', views.chat_send_message, name='send_message'),
    path('delete/<int:message_pk>/', views.chat_delete_message, name='delete_message'),
    path('highlight/<int:message_pk>/', views.chat_toggle_highlight, name='toggle_highlight'),
]
