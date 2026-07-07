from django import forms
from .models import Entidad


class EntidadForm(forms.ModelForm):

    class Meta:
        model = Entidad
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "responsable",
            "estado",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "nombre": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "responsable": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "estado": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }