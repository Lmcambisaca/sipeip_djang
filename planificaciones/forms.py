from django import forms
from .models import Planificacion


class PlanificacionForm(forms.ModelForm):

    class Meta:

        model = Planificacion

        fields = [
            "periodo",
            "nombre",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "entidad",
            "observacion",
        ]

        widgets = {

            "periodo": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "nombre": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "fecha_inicio": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),

            "fecha_fin": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),

            "estado": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

            "entidad": forms.Select(attrs={
                "class": "form-control"
            }),
            "observacion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
        }

def clean(self):

    cleaned_data = super().clean()

    periodo = cleaned_data.get("periodo")
    nombre = cleaned_data.get("nombre")
    descripcion = cleaned_data.get("descripcion")
    fecha_inicio = cleaned_data.get("fecha_inicio")
    fecha_fin = cleaned_data.get("fecha_fin")

    if periodo:
        cleaned_data["periodo"] = periodo.strip()

    if nombre:
        cleaned_data["nombre"] = nombre.strip()

    if descripcion:
        cleaned_data["descripcion"] = descripcion.strip()

    if fecha_inicio and fecha_fin:

        if fecha_inicio > fecha_fin:

            raise forms.ValidationError(
                "La fecha de inicio no puede ser mayor que la fecha de fin."
            )

    if nombre:

        existe = Planificacion.objects.filter(
            nombre__iexact=nombre
        )

        if self.instance.pk:

            existe = existe.exclude(
                pk=self.instance.pk
            )

        if existe.exists():

            raise forms.ValidationError(
                "Ya existe una planificación con ese nombre."
            )

    return cleaned_data