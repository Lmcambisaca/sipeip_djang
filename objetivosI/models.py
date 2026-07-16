from django.db import models

from proyectos.models import Proyecto
from usuarios.models import Usuario


class ObjetivoInstitucional(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    descripcion = models.TextField()

    periodo_vigencia = models.CharField(
        max_length=20
    )

    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )

    estado = models.BooleanField(
        default=True
    )

    proyectos = models.ManyToManyField(
        Proyecto,
        blank=True,
        related_name="objetivos_institucionales"
    )

    class Meta:

        db_table = "objetivo_institucional"

        verbose_name = "Objetivo Institucional"

        verbose_name_plural = "Objetivos Institucionales"

    def __str__(self):

        return self.codigo


class HistorialObjetivoInstitucional(models.Model):

    objetivo = models.ForeignKey(
        ObjetivoInstitucional,
        on_delete=models.CASCADE
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )

    accion = models.CharField(
        max_length=100
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = "historial_objetivo_institucional"

    def __str__(self):

        return f"{self.objetivo.codigo} - {self.accion}"