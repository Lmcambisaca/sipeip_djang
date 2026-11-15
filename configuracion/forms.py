from django import forms

from .models import Configuracion


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = (
            "categoria",
            "nombre",
            "valor",
            "descripcion",
            "estado",
        )
        widgets = {
            "categoria": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_categoria(self):
        categoria = self.cleaned_data["categoria"].strip()
        if not categoria:
            raise forms.ValidationError("La categoría es obligatoria.")
        return categoria

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")

        existentes = Configuracion.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise forms.ValidationError(
                "Ya existe un parámetro con ese nombre."
            )

        return nombre

    def clean_valor(self):
        valor = self.cleaned_data["valor"].strip()
        if not valor:
            raise forms.ValidationError("El valor es obligatorio.")
        return valor

    def clean_descripcion(self):
        descripcion = self.cleaned_data["descripcion"].strip()
        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")
        return descripcion