from django import forms

from .models import Entidad


class EntidadForm(forms.ModelForm):
    class Meta:
        model = Entidad
        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "responsable",
        )
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "responsable": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"].strip()

        if not codigo:
            raise forms.ValidationError("El código es obligatorio.")

        existentes = Entidad.objects.filter(codigo__iexact=codigo)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise forms.ValidationError(
                "Ya existe una entidad con ese código."
            )

        return codigo

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data["descripcion"].strip()
        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")
        return descripcion

    def clean_responsable(self):
        responsable = self.cleaned_data["responsable"].strip()
        if not responsable:
            raise forms.ValidationError("El responsable es obligatorio.")
        return responsable