from django import forms

from .models import ObjetivoEstrategico


class ObjetivoEstrategicoForm(forms.ModelForm):

    class Meta:

        model = ObjetivoEstrategico

        fields = (

            "codigo",

            "descripcion",

            "eje_estrategico",

            "periodo_vigencia",

            "estado",

            "objetivos_institucionales"

        )

        widgets = {

            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control"
                }
            ),

            "eje_estrategico": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "periodo_vigencia": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "estado": forms.CheckboxInput(),

            "objetivos_institucionales": forms.SelectMultiple(
                attrs={
                    "class": "form-select"
                }
            )

        }