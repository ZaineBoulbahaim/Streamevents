from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Llistat d'esdeveniments
    path('', views.event_list_view, name='event_list'),
    
    # Crear esdeveniment
    path('create/', views.event_create_view, name='event_create'),
    
    # Detall d'esdeveniment
    path('<int:pk>/', views.event_detail_view, name='event_detail'),
    
    # Editar esdeveniment
    path('<int:pk>/edit/', views.event_update_view, name='event_update'),
    
    # Eliminar esdeveniment
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),
    
    # Els meus esdeveniments
    path('my-events/', views.my_events_view, name='my_events'),
    
    # Esdeveniments per categoria
    path('category/<str:category>/', views.events_by_category_view, name='events_by_category'),
    
    # URL para autocompletar etiquetas
    path('api/tags/autocomplete/', views.get_tags_autocomplete, name='tags_autocomplete'),
]