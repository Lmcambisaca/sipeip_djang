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

        for campo in ("periodo", "nombre", "descripcion"):
            valor = cleaned_data.get(campo)

            if valor:
                valor = valor.strip()
                cleaned_data[campo] = valor

                if not valor:
                    self.add_error(campo, "Este campo es obligatorio.")

        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error(
                "fecha_fin",
                "La fecha de fin no puede ser anterior a la fecha de inicio.",
            )

        nombre = cleaned_data.get("nombre")

        if nombre:
            existentes = Planificacion.objects.filter(nombre__iexact=nombre)

            if self.instance.pk:
                existentes = existentes.exclude(pk=self.instance.pk)

            if existentes.exists():
                self.add_error(
                    "nombre",
                    "Ya existe una planificación con ese nombre.",
                )

        return cleaned_data