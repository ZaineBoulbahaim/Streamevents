from django.contrib import admin
from django.urls import path, include
from users.views import home_view, login_view
from django.contrib.auth import views as auth_views
from users.forms import CustomPasswordResetForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    
    # URL de login duplicada en nivel principal
    path('login/', login_view, name='login'),
    
    # URLs de autenticación en el nivel principal
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             form_class=CustomPasswordResetForm,
             success_url='done/'
         ), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/reset/done/'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # URLs de la app users con prefijo
    path('users/', include('users.urls', namespace='users')),
]