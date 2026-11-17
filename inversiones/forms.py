from django import forms

from proyectos.models import Proyecto
from .models import Inversion


class InversionForm(forms.ModelForm):
    class Meta:
        model = Inversion
        fields = (
            "codigo",
            "nombre",
            "monto_asignado",
            "fuente_financiamiento",
            "proyecto",
            "periodo_fiscal",
            "estado",
        )
        widgets = {
            "codigo": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "monto_asignado": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "fuente_financiamiento": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "proyecto": forms.Select(
                attrs={"class": "form-select"}
            ),
            "periodo_fiscal": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1000",
                    "max": "9999",
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proyecto"].queryset = Proyecto.objects.filter(
            eliminado=False,
            estado=True
        )

    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"].strip()

        consulta = Inversion.objects.filter(
            codigo__iexact=codigo
        )
        
        if self.instance.pk:
            consulta = consulta.exclude(pk=self.instance.pk)

        if consulta.exists():
            raise forms.ValidationError(
                "Ya existe una inversión con ese código."
            )

        return codigo

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        
        if not nombre:
            raise forms.ValidationError(
                "El nombre de la inversión es obligatorio."
            )
        
        return nombre

    def clean_fuente_financiamiento(self):
        
        fuente = self.cleaned_data["fuente_financiamiento"].strip()
        
        if not fuente:
            raise forms.ValidationError(
                "La fuente de financiamiento es obligatoria."
            )
        
        return fuente

    def clean_monto_asignado(self):
        monto = self.cleaned_data["monto_asignado"]
        
        if monto <= 0:
            raise forms.ValidationError(
                "El monto asignado debe ser mayor que cero."
            )
        
        return monto

    def clean_periodo_fiscal(self):
        
        periodo = self.cleaned_data["periodo_fiscal"]
        
        if periodo < 1000 or periodo > 9999:
            raise forms.ValidationError(
                "Ingresa un período fiscal de cuatro dígitos."
            )
        
        return periodo


class ConsultaInversionForm(forms.Form):
    ESTADOS = (
        ("", "Todos"),
        ("true", "Activas"),
        ("false", "Inactivas"),
    )

    periodo_fiscal = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=9999,
        label="Período fiscal",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1000", "max": "9999"}
        )
    )
    fuente_financiamiento = forms.CharField(
        required=False,
        label="Fuente de financiamiento",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    estado = forms.ChoiceField(
        required=False,
        choices=ESTADOS,
        label="Estado",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    proyecto = forms.ModelChoiceField(
        required=False,
        queryset=Proyecto.objects.filter(eliminado=False),
        empty_label="Todos los proyectos",
        label="Proyecto",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    monto_minimo = forms.DecimalField(
        required=False,
        min_value=0,
        label="Monto mínimo asignado",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0"}
        )
    )
    monto_maximo = forms.DecimalField(
        required=False,
        min_value=0,
        label="Monto máximo asignado",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0"}
        )
    )

    def clean(self):
        datos = super().clean()
        minimo = datos.get("monto_minimo")
        maximo = datos.get("monto_maximo")

        if minimo is not None and maximo is not None and minimo > maximo:
            self.add_error(
                "monto_maximo",
                "El monto máximo debe ser igual o mayor que el mínimo."
            )

        return datos
    
class EditarInversionForm(forms.ModelForm):
    class Meta:
        model = Inversion
        fields = (
            "monto_asignado",
            "monto_ejecutado",
            "fuente_financiamiento",
            "estado",
        )
        widgets = {
            "monto_asignado": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "monto_ejecutado": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "fuente_financiamiento": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean(self):
        datos = super().clean()
        asignado = datos.get("monto_asignado")
        ejecutado = datos.get("monto_ejecutado")

        if asignado is not None and asignado <= 0:
            self.add_error(
                "monto_asignado",
                "El monto asignado debe ser mayor que cero."
            )

        if ejecutado is not None and ejecutado < 0:
            self.add_error(
                "monto_ejecutado",
                "El monto ejecutado no puede ser negativo."
            )

        if (
            asignado is not None
            and ejecutado is not None
            and ejecutado > asignado
        ):
            self.add_error(
                "monto_ejecutado",
                "El monto ejecutado no puede superar el monto asignado."
            )

        fuente = datos.get("fuente_financiamiento")
        if fuente and not fuente.strip():
            self.add_error(
                "fuente_financiamiento",
                "La fuente de financiamiento es obligatoria."
            )
        elif fuente:
            datos["fuente_financiamiento"] = fuente.strip()

        return datos