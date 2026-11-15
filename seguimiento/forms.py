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
    
    def clean(self):
        cleaned_data = super().clean()

        for campo in ("descripcion", "periodo", "unidad_medida"):
            valor = cleaned_data.get(campo)
            if valor and not valor.strip():
                self.add_error(campo, "Este campo no puede quedar vacío.")

        valor_esperado = cleaned_data.get("valor_esperado")
        if valor_esperado is not None and valor_esperado <= 0:
            self.add_error(
                "valor_esperado",
                "El valor esperado debe ser mayor que cero."
            )

        return cleaned_data
        
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
            
    def clean(self):
        cleaned_data = super().clean()

        for campo in ("nombre", "formula", "unidad_medida", "frecuencia"):
            valor = cleaned_data.get(campo)
            if valor and not valor.strip():
                self.add_error(campo, "Este campo no puede quedar vacío.")

        return cleaned_data
        
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
        
    def clean(self):
        cleaned_data = super().clean()

        valor = cleaned_data.get("valor")
        if valor is not None and valor < 0:
            self.add_error("valor", "El valor del avance no puede ser negativo.")

        return cleaned_data