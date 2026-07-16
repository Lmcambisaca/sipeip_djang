from django import forms

from .models import ObjetivoInstitucional


class ObjetivoInstitucionalForm(forms.ModelForm):

    class Meta:

        model = ObjetivoInstitucional

        fields = (

            "codigo",

            "descripcion",

            "periodo_vigencia",

            "responsable",

            "estado",

            "proyectos"

        )

        widgets = {

            "codigo": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class":"form-control"
                }
            ),

            "periodo_vigencia": forms.TextInput(
                attrs={
                    "class":"form-control"
                }
            ),

            "responsable": forms.Select(
                attrs={
                    "class":"form-select"
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class":"form-check-input"
                }
            ),

            "proyectos": forms.SelectMultiple(
                attrs={
                    "class":"form-select"
                }
            )

        }