from django import forms
from .models import ChatMessage

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Escriu el teu missatge...',
                    'maxlength': 500,
                }
            )
        }
    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()

        if not message:
            raise forms.ValidationError(
                'El missatge no pot estar buit.'
            )

        forbidden_words = [
            'idiota',
            'tonto',
            'mierda',
            'puta',
        ]

        lower_message = message.lower()

        for word in forbidden_words:
            if word in lower_message:
                raise forms.ValidationError(
                    'El missatge conté paraules ofensives.'
                )

        if len(message) > 500:
            raise forms.ValidationError(
                'El missatge no pot superar els 500 caràcters.'
            )

        return message
