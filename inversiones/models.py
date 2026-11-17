from django.core.validators import MinValueValidator
from django.db import models

from proyectos.models import Proyecto
from usuarios.models import Usuario



class Inversion(models.Model):
    codigo = models.CharField(
        max_length=30,
        unique=True
    )
    nombre = models.CharField(
        max_length=200
    )
    monto_asignado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    monto_ejecutado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    fuente_financiamiento = models.CharField(
        max_length=150
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.PROTECT,
        related_name="inversiones"
    )
    periodo_fiscal = models.PositiveSmallIntegerField()
    estado = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "inversion"
        ordering = ["periodo_fiscal", "codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def monto_pendiente(self):
        return self.monto_asignado - self.monto_ejecutado

    @property
    def porcentaje_ejecucion(self):
        if self.monto_asignado <= 0:
            return 0

        return round(
            self.monto_ejecutado / self.monto_asignado * 100,
            2
        )


class HistorialInversion(models.Model):
    inversion = models.ForeignKey(
        Inversion,
        on_delete=models.CASCADE,
        related_name="historial"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )
    accion = models.CharField(max_length=250)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "historial_inversion"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.inversion.codigo} - {self.accion}"