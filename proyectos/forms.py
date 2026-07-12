from django import forms

from .models import Proyecto, Cronograma, Documento


class ProyectoForm(forms.ModelForm):

    class Meta:

        model = Proyecto

        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "responsable",
            "presupuesto",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "planificacion",
        )

        widgets = {

            "codigo": forms.TextInput(attrs={"class": "form-control"}),

            "nombre": forms.TextInput(attrs={"class": "form-control"}),

            "descripcion": forms.Textarea(attrs={"class": "form-control"}),

            "responsable": forms.Select(attrs={"class": "form-select"}),

            "presupuesto": forms.NumberInput(attrs={"class": "form-control"}),

            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "planificacion": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }


class CronogramaForm(forms.ModelForm):

    class Meta:

        model = Cronograma

        fields = (
            "proyecto",
            "actividad",
            "responsable",
            "fecha_inicio",
            "fecha_fin",
            "estado",
        )

        widgets = {

            "proyecto": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "actividad": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "responsable": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "porcentaje_avance": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

        }
        
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["proyecto"].queryset = Proyecto.objects.filter(
        eliminado=False
        )
        
class DocumentoForm(forms.ModelForm):

    class Meta:

        model = Documento

        fields = (

            "proyecto",

            "nombre",

            "descripcion",

            "archivo",

        )

        widgets = {

            "proyecto": forms.Select(
                attrs={"class": "form-select"}
            ),

            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "descripcion": forms.Textarea(
                attrs={"class": "form-control"}
            ),

            "archivo": forms.FileInput(
                attrs={"class": "form-control"}
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["proyecto"].queryset = Proyecto.objects.filter(
            eliminado=False
        )