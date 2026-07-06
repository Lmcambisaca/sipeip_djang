from django import forms
from .models import Rol


class RolForm(forms.ModelForm):

    class Meta:
        model = Rol
        fields = ["nombre", "descripcion", "estado"]

        widgets = {
            "nombre": forms.TextInput(attrs={
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