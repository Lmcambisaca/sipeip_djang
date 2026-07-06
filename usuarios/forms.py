from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class UsuarioForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'rol',
            'estado',
        ]


class UsuarioEditarForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'email',
            'rol',
            'estado',
        ]
        
class RecuperarPasswordForm(forms.Form):

    email = forms.EmailField(
        label="Correo electrónico"
    )

    nueva_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Nueva contraseña"
    )

    confirmar_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña"
    )