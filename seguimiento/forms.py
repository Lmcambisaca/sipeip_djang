from django import forms
from .models import Meta
from proyectos.models import Proyecto
from .models import Indicador, AvanceIndicador


class MetaForm(forms.ModelForm):

    class Meta:

        model = Meta

        fields = (

            "proyecto",

            "descripcion",

            "periodo",

            "unidad_medida",

            "valor_esperado",

            "estado",

        )

        widgets = {

            "proyecto": forms.Select(
                attrs={"class":"form-select"}
            ),

            "descripcion": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "periodo": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "unidad_medida": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "valor_esperado": forms.NumberInput(
                attrs={"class":"form-control"}
            ),

            "estado": forms.CheckboxInput(
                attrs={"class":"form-check-input"}
            ),

        }

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.fields["proyecto"].queryset = Proyecto.objects.filter(
            eliminado=False
        )
        
class IndicadorForm(forms.ModelForm):

    class Meta:

        model = Indicador

        fields = (

            "meta",

            "nombre",

            "formula",

            "unidad_medida",

            "frecuencia",

            "estado",

        )

        widgets={

            "meta":forms.Select(
                attrs={"class":"form-select"}
            ),

            "nombre":forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "formula":forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "unidad_medida":forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "frecuencia":forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "estado":forms.CheckboxInput(
                attrs={"class":"form-check-input"}
            )

        }
        
class AvanceIndicadorForm(forms.ModelForm):

    class Meta:

        model = AvanceIndicador

        fields=(

            "indicador",

            "fecha",

            "valor",

        )

        widgets={

            "indicador":forms.Select(
                attrs={"class":"form-select"}
            ),

            "fecha":forms.DateInput(
                attrs={
                    "class":"form-control",
                    "type":"date"
                }
            ),

            "valor":forms.NumberInput(
                attrs={
                    "class":"form-control"
                }
            )

        }