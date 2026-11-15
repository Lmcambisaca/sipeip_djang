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
        
    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip()

    def clean_descripcion(self):
        return self.cleaned_data["descripcion"].strip()

    def clean_eje_estrategico(self):
        return self.cleaned_data["eje_estrategico"].strip()

    def clean_periodo_vigencia(self):
        return self.cleaned_data["periodo_vigencia"].strip()