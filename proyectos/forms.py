from django import forms

from .models import Proyecto, Cronograma, Documento


class ProyectoForm(forms.ModelForm):
    
    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"].strip()

        existentes = Proyecto.objects.filter(codigo__iexact=codigo)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)

        if existentes.exists():
            raise forms.ValidationError(
                "Ya existe un proyecto con ese código."
            )

        return codigo

    def clean_presupuesto(self):
        presupuesto = self.cleaned_data["presupuesto"]
        if presupuesto <= 0:
            raise forms.ValidationError(
                "El presupuesto debe ser mayor que cero."
            )
        return presupuesto

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error(
                "fecha_fin",
                "La fecha de fin no puede ser anterior a la fecha de inicio.",
            )

        return cleaned_data

    class Meta:

        model = Proyecto

        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "responsable",
            "presupuesto",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "planificacion",
        )

        widgets = {

            "codigo": forms.TextInput(attrs={"class": "form-control"}),

            "nombre": forms.TextInput(attrs={"class": "form-control"}),

            "descripcion": forms.Textarea(attrs={"class": "form-control"}),

            "responsable": forms.Select(attrs={"class": "form-select"}),

            "presupuesto": forms.NumberInput(attrs={"class": "form-control"}),

            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "planificacion": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }


class CronogramaForm(forms.ModelForm):
    
    class Meta:
        
        model = Cronograma
        
        fields = (
            "proyecto",
            "actividad",
            "responsable",
            "fecha_inicio",
            "fecha_fin",
            "estado",
        )
        
        widgets = {
        
            "proyecto": forms.Select(
                attrs={"class": "form-select"}
            ),
        
            "actividad": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        
            "responsable": forms.Select(
                attrs={"class": "form-select"}
            ),
        
            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        
            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        
            "estado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        
        }

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.fields["proyecto"].queryset = Proyecto.objects.filter(
            eliminado=False
        )

    def clean(self):
        cleaned_data = super().clean()
        actividad = cleaned_data.get("actividad")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if actividad:
            actividad = actividad.strip()
            if not actividad:
                self.add_error("actividad", "La actividad es obligatoria.")
            cleaned_data["actividad"] = actividad

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error(
                "fecha_fin",
                "La fecha de fin no puede ser anterior a la fecha de inicio.",
            )

        return cleaned_data
        
class DocumentoForm(forms.ModelForm):
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")

        if archivo:
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "El archivo no puede superar los 5 MB."
                )

            extension = archivo.name.rsplit(".", 1)[-1].lower()
            permitidas = {
                "pdf", "doc", "docx", "xls", "xlsx",
                "png", "jpg", "jpeg",
            }

            if extension not in permitidas:
                raise forms.ValidationError(
                    "Formato no permitido. Use PDF, Office o imagen."
                )

        return archivo

    class Meta:

        model = Documento

        fields = (

            "proyecto",

            "nombre",

            "descripcion",

            "archivo",

        )

        widgets = {

            "proyecto": forms.Select(
                attrs={"class": "form-select"}
            ),

            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "descripcion": forms.Textarea(
                attrs={"class": "form-control"}
            ),

            "archivo": forms.FileInput(
                attrs={"class": "form-control"}
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["proyecto"].queryset = Proyecto.objects.filter(
            eliminado=False
        )