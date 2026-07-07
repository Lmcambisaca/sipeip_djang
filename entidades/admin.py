from django.contrib import admin
from .models import Entidad


@admin.register(Entidad)
class EntidadAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "nombre",
        "responsable",
        "estado"
    )

    search_fields = (
        "codigo",
        "nombre"
    )