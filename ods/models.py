from django.db import models

from proyectos.models import Proyecto

from usuarios.models import Usuario



class ObjetivoDesarrollo(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    descripcion = models.TextField()

    eje_estrategico = models.CharField(
        max_length=200
    )

    periodo_vigencia = models.CharField(
        max_length=100
    )

    proyectos = models.ManyToManyField(
        Proyecto,
        blank=True,
        related_name="objetivos_desarrollo"
    )
    
    class Meta:

        db_table = "objetivo_desarrollo"

        verbose_name = "Objetivo de Desarrollo"

        verbose_name_plural = "Objetivos de Desarrollo"

    def __str__(self):

        return f"{self.codigo} - {self.descripcion}"
    
class HistorialObjetivo(models.Model):

    objetivo = models.ForeignKey(
        ObjetivoDesarrollo,
        on_delete=models.CASCADE,
        related_name="historial"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    descripcion = models.CharField(
        max_length=250
    )

    class Meta:

        db_table = "historial_objetivo"

        verbose_name = "Historial Objetivo"

        verbose_name_plural = "Historial Objetivos"

    def __str__(self):

        return f"{self.objetivo.codigo} - {self.fecha}"