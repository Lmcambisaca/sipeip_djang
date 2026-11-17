from django import forms

from .models import Reporte


class ReporteForm(forms.ModelForm):
    busqueda = forms.CharField(
        required=False,
        label="Texto a buscar",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    periodo = forms.CharField(
        required=False,
        label="Período",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    estado = forms.ChoiceField(
        required=False,
        choices=(
            ("", "Todos"),
            ("true", "Activo/aprobado"),
            ("false", "Inactivo/no aprobado"),
        ),
        label="Estado",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Reporte
        fields = ("tipo",)
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"})
        }