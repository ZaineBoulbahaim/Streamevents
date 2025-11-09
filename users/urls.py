from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'users'  # Esto permite usar {% url 'users:login' %}

urlpatterns = [
    path('', views.home_view, name='home'), # Pagina principal
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),
    
    
    # Password reset flow (Django built-in views; templates a registration/)
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'
    )
]