from django.db import models
from django.conf import settings


class Reporte(models.Model):

    TIPO_REPORTE = [

        ("Usuarios", "Usuarios"),
        ("Entidades", "Entidades"),
        ("Planificaciones", "Planificaciones"),
        ("Proyectos", "Proyectos"),
        ("ODS", "ODS"),
        ("Metas", "Metas"),
        ("Indicadores", "Indicadores"),
        ("Avances", "Avances"),

    ]

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_REPORTE
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    fecha_generacion = models.DateTimeField(
        auto_now_add=True
    )

    archivo_pdf = models.FileField(
        upload_to="reportes/pdf/",
        blank=True,
        null=True
    )

    archivo_excel = models.FileField(
        upload_to="reportes/excel/",
        blank=True,
        null=True
    )

    class Meta:

        db_table = "reporte"

        verbose_name = "Reporte"

        verbose_name_plural = "Reportes"

    def __str__(self):

        return f"{self.tipo} - {self.fecha_generacion:%d/%m/%Y}"