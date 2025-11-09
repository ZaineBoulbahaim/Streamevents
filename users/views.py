# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError

User = get_user_model()

def home_view(request):
    """
    Vista principal de la aplicación StreamEvents
    Es mostrarà com a portada quan entrem a la web.
    """
    return render(request, 'users/home.html')


# Función que gestiona el registro, esta será llamada siempre que se quiera registrar alguien.
def register_view(request):
    """
    Registro de usuario compatible con Djongo.
    Captura errores de duplicado directamente al guardar.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f"T'has registrat correctament! Benvingut/da, {user.username}")
                return redirect('users:profile')
            except DatabaseError:
                messages.error(request, "Aquest email o nom d'usuari ja està registrat.")
        else:
            messages.error(request, "El teu compte no s'ha creat correctament. Revisa el formulari.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """
    Vista para el inicio de sesión
    """
    # Si se ha enviado el formulario, es decir, POST
    if request.method == 'POST':
        # Creamos el formulario con los datos recibidos
        form = CustomAuthenticationForm(request, data=request.POST)
        # Si el formulario es valido.
        if form.is_valid():
            # Obtenemos el usuario
            user = form.get_user()
            # Iniciamos sesión
            login(request, user)
            # Mostramos un mensaje
            messages.success(request, f"Benvingut de nou, {user.username}!")
            # Dirigimos al perfil del usuario
            return redirect('users:profile')
        else:
            messages.error(request, "Credencials incorrectes. Torna-ho a provar.")
    else:
        # En caso que el formulario este vacio, lo mostramos
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# Función para cerrar la sessión
def logout_view(request):
    """
    Cierra la sesión y redirige a la pàgina principal
    """
    # Cierra la sesión
    logout(request)

    # Muestra mensaje 
    messages.info(request, "Has tancat la sessió correctament.")

    # Redirigimos a la pàgina principal
    return redirect('users:home')


# Comprobamos que el usuario este autenticado gracias al request.user.is_authenticated
@login_required
def profile_view(request):
    """
    Muestra el perfil del usuario
    """
    # Obtenemos el usuario
    user = request.user

    # Preparamos el context para poder usarlo en la pàgina
    context = {
        'user': user
    }

    # Renderizamos la pàgina con el context
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    """
    Vista para editar el perfil
    """
    # Usuario actual
    user = request.user
    
    # En caso que se quiera editar
    if request.method == 'POST':
        # Creamos el formulario
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        # Si todo esta correcto
        if form.is_valid():
            form.save()
            # Mostramos mensaje y redirigimos
            messages.success(request, "Perfil actualitzat correctament!")
            return redirect('users:profile')
        # En caso contrario, mostramos mensaje de error.
        else:
            messages.error(request, "Hi ha hagut un error en actualitzar el perfil. Torna-ho a provar.")
    else:
        form = CustomUserUpdateForm(instance=user)

    return render(request, 'users/edit_profile.html', {'form': form})

def public_profile_view(request, username):
    """
    Vista para ver el perfil de otro usuario
    """
    # Obtenemos el usuario
    user = get_object_or_404(get_user_model(), username=username)

    # Renderizamos la pàgina con el context
    return render(request, 'users/public_profile.html', {'profile_user': user})