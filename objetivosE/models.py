from django.db import models

from objetivosI.models import ObjetivoInstitucional
from usuarios.models import Usuario


class ObjetivoEstrategico(models.Model):

    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    descripcion = models.TextField()

    eje_estrategico = models.CharField(
        max_length=150
    )

    periodo_vigencia = models.CharField(
        max_length=50
    )

    estado = models.BooleanField(
        default=True
    )

    objetivos_institucionales = models.ManyToManyField(
        ObjetivoInstitucional,
        blank=True,
        related_name="objetivos_estrategicos"
    )

    class Meta:

        db_table = "objetivo_estrategico"

        verbose_name = "Objetivo Estratégico"

        verbose_name_plural = "Objetivos Estratégicos"

    def __str__(self):

        return self.codigo
    

class HistorialObjetivoEstrategico(models.Model):

    objetivo = models.ForeignKey(
        ObjetivoEstrategico,
        on_delete=models.CASCADE
    )

    accion = models.CharField(
        max_length=200
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )

    class Meta:

        db_table = "historial_objetivo_estrategico"

    def __str__(self):

        return self.accion