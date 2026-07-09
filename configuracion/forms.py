from django import forms
from .models import Configuracion


class ConfiguracionForm(forms.ModelForm):

    class Meta:

        model = Configuracion

        fields = "__all__"

        widgets = {

            "nombre": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "valor": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "estado": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            })

        }