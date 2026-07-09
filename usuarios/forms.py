from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from roles.models import Rol

User = get_user_model()


class UsuarioForm(UserCreationForm):

    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    email = forms.EmailField(
        label="Correo",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control"
        })
    )

    username = forms.CharField(
        label="Usuario",
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    rol = forms.ModelChoiceField(
        queryset=Rol.objects.filter(estado=True),
        empty_label="Seleccione un rol",
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    estado = forms.BooleanField(
        required=False,
        initial=True
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:

        model = User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "rol",
            "estado",
            "password1",
            "password2",
        )

    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():

            raise forms.ValidationError(
                "Ya existe un usuario con este correo."
            )

        return email


class UsuarioEditarForm(forms.ModelForm):

    class Meta:

        model = User

        fields = (
            "first_name",
            "last_name",
            "email",
            "rol",
            "estado",
        )

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "rol": forms.Select(attrs={
                "class": "form-select"
            })

        }

    def clean_email(self):

        email = self.cleaned_data["email"]

        existe = User.objects.filter(
            email__iexact=email
        ).exclude(
            id=self.instance.id
        )

        if existe.exists():

            raise forms.ValidationError(
                "Ya existe un usuario con ese correo."
            )

        return email


class RecuperarPasswordForm(forms.Form):

    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={
            "class": "form-control"
        })
    )

    nueva_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )