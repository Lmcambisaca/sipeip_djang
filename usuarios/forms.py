from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model


from roles.models import Rol
from entidades.models import Entidad

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
    
    identificacion = forms.CharField(
        label="Identificación",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    cargo = forms.CharField(
        label="Cargo",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    entidad = forms.ModelChoiceField(
        label="Entidad",
        queryset=Entidad.objects.filter(estado=True).order_by("nombre"),
        empty_label="Seleccione una entidad",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
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
            "identificacion",
            "cargo",
            "email",
            "entidad",
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
    
    def clean_identificacion(self):
        identificacion = self.cleaned_data["identificacion"].strip()

        existe = User.objects.filter(
            identificacion__iexact=identificacion
        ).exists()

        if existe:
            raise forms.ValidationError(
                "Ya existe un usuario con esa identificación."
            )

        return identificacion


class UsuarioEditarForm(forms.ModelForm):
    
    class UsuarioEditarForm(forms.ModelForm):
        
        identificacion = forms.CharField(
        label="Identificación",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    cargo = forms.CharField(
        label="Cargo",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    entidad = forms.ModelChoiceField(
        label="Entidad",
        queryset=Entidad.objects.all().order_by("nombre"),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        
        model = User
        
        fields = (
            "first_name",
            "last_name",
            "identificacion",
            "cargo",
            "email",
            "entidad",
            "rol",
            "estado",
        )
        
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        existe = User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        )

        if existe.exists():
            raise forms.ValidationError(
                "Ya existe un usuario con ese correo."
            )

        return email

    def clean_identificacion(self):
        identificacion = self.cleaned_data["identificacion"].strip()

        existe = User.objects.filter(
            identificacion__iexact=identificacion
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if existe:
            raise forms.ValidationError(
                "Ya existe otro usuario con esa identificación."
            )

        return identificacion
        
    def clean_identificacion(self):
        identificacion = self.cleaned_data["identificacion"].strip()

        existe = User.objects.filter(
            identificacion__iexact=identificacion
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if existe:
            raise forms.ValidationError(
                "Ya existe otro usuario con esa identificación."
            )

        return identificacion

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
    
    password_actual = forms.CharField(
    label="Contraseña actual",
    widget=forms.PasswordInput(
        attrs={
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
    
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su correo electrónico",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su contraseña",
            }
        ),
    )

    def clean(self):
        email = self.cleaned_data.get("username")

        if email:
            usuario = User.objects.filter(email__iexact=email).only("username").first()
            if usuario:
                # AuthenticationForm autentica usando el nombre de usuario.
                self.cleaned_data["username"] = usuario.get_username()

        return super().clean()