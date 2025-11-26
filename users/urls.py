from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm


app_name = 'users'  # Esto permite usar {% url 'users:login' %}

urlpatterns = [
    path('', views.home_view, name='home'), # Pagina principal
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),
]