from django import forms
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re, imghdr
from django.contrib.auth.forms import AuthenticationForm
# útil para las traducciones
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

# Obtenemos el modelo de ususario que esta configurado en nuestro proyecto
# Esta configurado en config/settings.py
User = get_user_model()

# Cremos un formulario vinculado al ModelForm
class  CustomUserCreationForm(forms.ModelForm):
    # Dos campos manuales para definir la contraseña
    # Con widget=forms para ocultar el texto introducido
    password1 = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={'placeholder': 'Introdueix la contrasenya: '})
    )
    password2 = forms.CharField(
        label="Confirma la contrasenya",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeteix la contrasenya: '})
    )
    
    # Campos que aparecen en el formulario
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    # Método para comprobar que no existe un usuario con ese mismo email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Aquest correu ja està registrat.")
        return email
    
    # Método para comprobar el nombre de usuario
    # Usamos re.match para expresiones regulares
    def clean_username(self):
        username = self.cleaned_data.get('username')
        pattern = r'^[\w.@+-]+$'
        if not re.match(pattern, username):
            raise ValidationError("El nom d'usuari només pot contenir lletres, números i @/./+/-/_")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Aquest nom d'usuari ja està registrat.")
        return username
    
    # Método que comprueba que la primera constraseña es igual a la segunda
    # Además debe tener un minímo de criterios para ser aceptada
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les contrasenyes no coincideixen.")
        
        # Validaciones complejas
        if password1:
            errors = []
            if len(password1) < 8:
                errors.append("La contrasenya ha de tenir almenys 8 caràcters.")
            if not re.search(r'[A-Z]', password1):
                errors.append("Ha de contenir almenys una lletra majúscula.")
            if not re.search(r'[a-z]', password1):
                errors.append("Ha de contenir almenys una lletra minúscula.")
            if not re.search(r'[0-9]', password1):
                errors.append("Ha de contenir almenys un número.")
            if not re.search(r'[@$!%*?&]', password1):
                errors.append("Ha de contenir almenys un caràcter especial (@, $, !, %, *, ?, &).")
            if errors:
                raise ValidationError(f"La contrasenya no és vàlida: {' '.join(errors)}")
        
        return cleaned_data
    
    # Definimos el método save y decimos que si queremos guardar inmediatamente en la base de datos
    def save(self, commit=True):
        # Creamos el objeto pero todavía no lo guardamos
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # Guardamos
        if commit:
            user.save()
        return user
        
        
class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Campos que puede editar el usuario en su perfil
        fields = ['first_name', 'last_name', 'display_name', 'bio', 'avatar']
        # Personalizamos como se ven los campos en los formularios
        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': _('Explica alguna cosa sobre tu...'),
                'rows': 4,
                'class': 'form-control',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control-file',
            }),
        }
    
    # Validamos que la iamgen no supera los 2 MB
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError("La imatge no pot superar els 2 MB.")
            if not imghdr.what(avatar):
                raise ValidationError("El fitxer ha de ser una imatge vàlida.")
        return avatar
    
# Creamos una subclase del formulario original de Django pero con personalizaciones propias
class CustomAuthenticationForm(AuthenticationForm):
    # Input para introducir el nombre del usuario
    username = forms.CharField(
        label =_("Nom d'usuari"),
        widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder': _("Introdueix el teu nom d'usuari")
        })
    )
    
    # Campo de la contraseña
    password = forms.CharField(
        label=_("Contrasenya"),
        strip=False,
        # Con PasswordInput hacemos que al escribir se vean puntos o astericos
        widget=forms.PasswordInput(attrs={
            'class' : 'form-control',
            'placeholder': _("Introdueix la teva contrasenya")
        }),
    )
    
    # Definimos los mensajes de error
    error_messages = {
        'invalid_login': _(
            "El nom d'usuari o la contrasenya no són correctes. "
            "Comprova les teves credencials."
        ),
        'inactive': _("Aquest compte està desactivat."),
    }
    
    # Método para comprobar usuario contraseña
    def clean(self):
        self.user_cache = None
        # Obtenemos el usuario y contraseña de los campos pertinentes
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Comprobamos si la entrada es con email
            if '@' in username:
                try:
                    # Buscamos el usuario con dicho email
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username # obtenemos su username real
                # En caso contrario, error 
                except User.DoesNotExist:
                    raise ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                    )
            # Autenticamos al usuario con las credenciales introducidas
            self.user_cache = authenticate(
                self.request,
                username = username,
                password = password
            )
            
            # Comprobamos si la autenticación ha fallado
            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data

