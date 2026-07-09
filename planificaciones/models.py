from django.db import models
from entidades.models import Entidad


class Planificacion(models.Model):

    periodo = models.CharField(
        max_length=20
    )

    nombre = models.CharField(
        max_length=200
    )

    descripcion = models.TextField()

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    estado = models.BooleanField(
        default=True
    )

    observacion = models.TextField(
        blank=True,
        default=""
    )

    validada = models.BooleanField(
        default=False
    )

    aprobada = models.BooleanField(
        default=False
    )
    
    aprobada_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planificaciones_aprobadas"
    )

    fecha_aprobacion = models.DateTimeField(
        null=True,
        blank=True
    )

    entidad = models.ForeignKey(
        Entidad,
        on_delete=models.PROTECT,
        related_name="planificaciones"
    )


    class Meta:

        db_table = "planificacion"

        verbose_name = "Planificación"

        verbose_name_plural = "Planificaciones"


    def __str__(self):

        return f"{self.periodo} - {self.nombre}"