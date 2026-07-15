from django import forms

from .models import ObjetivoDesarrollo


class ObjetivoDesarrolloForm(forms.ModelForm):

    class Meta:

        model = ObjetivoDesarrollo

        fields = (

            "codigo",

            "descripcion",

            "eje_estrategico",

            "periodo_vigencia",

            "proyectos",          

        )

        widgets = {

    "codigo": forms.TextInput(
        attrs={"class": "form-control"}
    ),

    "descripcion": forms.Textarea(
        attrs={"class": "form-control"}
    ),

    "eje_estrategico": forms.TextInput(
        attrs={"class": "form-control"}
    ),

    "periodo_vigencia": forms.TextInput(
        attrs={"class": "form-control"}
    ),

    "proyectos": forms.SelectMultiple(
        attrs={"class": "form-select"}
    ),
}