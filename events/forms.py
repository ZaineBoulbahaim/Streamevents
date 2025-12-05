from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Event

class EventCreationForm(forms.ModelForm):
    """
    Formulari per crear nous esdeveniments
    """
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 
                  'thumbnail', 'max_viewers', 'tags', 'stream_url']
        
        widgets = {
            'scheduled_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Descriu el teu esdeveniment...'
                }
            ),
            'thumbnail': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Títol de l\'esdeveniment'
                }
            ),
            'max_viewers': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'max': '1000'
                }
            ),
            'tags': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'gaming, música, esports...'
                }
            ),
            'stream_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://www.youtube.com/watch?v=... o https://www.twitch.tv/...'
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean_scheduled_date(self):
        """
        Validar que la data programada no sigui en el passat
        """
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if scheduled_date and scheduled_date < timezone.now():
            raise ValidationError("La data programada no pot ser en el passat.")
        
        return scheduled_date
    
    def clean_title(self):
        """
        Validar que el títol sigui únic per usuari
        """
        title = self.cleaned_data.get('title')
        
        if self.user and title:
            # Comprovar si l'usuari ja té un esdeveniment amb aquest títol
            existing_event = Event.objects.filter(
                creator=self.user, 
                title__iexact=title
            ).exists()
            
            if existing_event:
                raise ValidationError("Ja tens un esdeveniment amb aquest títol.")
        
        return title
    
    def clean_max_viewers(self):
        """
        Validar que el màxim d'espectadors estigui entre 1 i 1000
        """
        max_viewers = self.cleaned_data.get('max_viewers')
        
        if max_viewers and (max_viewers < 1 or max_viewers > 1000):
            raise ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        
        return max_viewers

class EventUpdateForm(forms.ModelForm):
    """
    Formulari per editar esdeveniments existents
    """
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 
                  'thumbnail', 'max_viewers', 'tags', 'status', 'stream_url']
        
        widgets = {
            'scheduled_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control'
                }
            ),
            'thumbnail': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        # Si l'esdeveniment ja està en directe, no es pot canviar la data
        if self.event and self.event.status == 'live':
            self.fields['scheduled_date'].disabled = True
            self.fields['scheduled_date'].help_text = "No es pot canviar la data mentre l'esdeveniment estigui en directe."
    
    def clean_status(self):
        """
        Validar que només el creador pugui canviar l'estat
        """
        status = self.cleaned_data.get('status')
        
        if self.user and self.event and self.user != self.event.creator:
            # Si l'usuari no és el creador, mantenir l'estat original
            return self.event.status
        
        return status
    
    def clean_scheduled_date(self):
        """
        Validar que no es pugui canviar la data si ja està en directe
        """
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if self.event and self.event.status == 'live':
            # Si ja està en directe, mantenir la data original
            return self.event.scheduled_date
        
        # Validar que la nova data no sigui en el passat
        if scheduled_date and scheduled_date < timezone.now():
            raise ValidationError("La data programada no pot ser en el passat.")
        
        return scheduled_date

class EventSearchForm(forms.Form):
    """
    Formulari per cercar i filtrar esdeveniments
    """
    
    # Choices per a categories (amb opció "Totes")
    CATEGORY_CHOICES_WITH_ALL = [('', 'Totes les categories')] + Event.CATEGORY_CHOICES
    
    # Choices per a estats (amb opció "Tots")
    STATUS_CHOICES_WITH_ALL = [('', 'Tots els estats')] + Event.STATUS_CHOICES
    
    # Camps del formulari
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Cerca per títol o descripció...',
                'aria-label': 'Cerca'
            }
        ),
        label='Cerca'
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES_WITH_ALL,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Categoria'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES_WITH_ALL,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Estat'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Des de'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fins a'
    )
    
    def clean(self):
        """
        Validacions addicionals
        """
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        # Validar que la data 'des de' no sigui posterior a la data 'fins a'
        if date_from and date_to and date_from > date_to:
            raise ValidationError("La data 'Des de' no pot ser posterior a la data 'Fins a'.")
        
        return cleaned_data