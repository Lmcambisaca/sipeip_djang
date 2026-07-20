from django.db import models
from proyectos.models import Proyecto


class Meta(models.Model):

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="metas"
    )

    descripcion = models.CharField(
        max_length=1000
    )

    periodo = models.CharField(
        max_length=20
    )

    unidad_medida = models.CharField(
        max_length=50
    )

    valor_esperado = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        db_table = "meta"

        verbose_name = "Meta"

        verbose_name_plural = "Metas"

    def __str__(self):

        return self.descripcion
    
class HistorialMeta(models.Model):

    meta = models.ForeignKey(
        Meta,
        on_delete=models.CASCADE
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    descripcion = models.TextField()

    class Meta:

        db_table = "historial_meta"

    def __str__(self):

        return self.meta.descripcion
    
class Indicador(models.Model):

    meta = models.ForeignKey(
        Meta,
        on_delete=models.CASCADE,
        related_name="indicadores"
    )

    nombre = models.CharField(
        max_length=1000
    )

    formula = models.CharField(
        max_length=200
    )

    unidad_medida = models.CharField(
        max_length=50
    )

    frecuencia = models.CharField(
        max_length=50
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        db_table = "indicador"

        verbose_name = "Indicador"

        verbose_name_plural = "Indicadores"

    def __str__(self):

        return self.nombre
    
class AvanceIndicador(models.Model):

    indicador = models.ForeignKey(
        Indicador,
        on_delete=models.CASCADE,
        related_name="avances"
    )

    fecha = models.DateField()

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    porcentaje_cumplimiento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    class Meta:

        db_table = "avance_indicador"

    def __str__(self):

        return self.indicador.nombre