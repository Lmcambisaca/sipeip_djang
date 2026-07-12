from django.db import models

from usuarios.models import Usuario
from planificaciones.models import Planificacion


class Proyecto(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=200
    )

    descripcion = models.TextField()

    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="proyectos"
    )

    presupuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    estado = models.BooleanField(
        default=True
    )
    
    eliminado = models.BooleanField(
    default=False
    )

    planificacion = models.ForeignKey(
        Planificacion,
        on_delete=models.PROTECT,
        related_name="proyectos"
    )

    class Meta:

        db_table = "proyecto"

        verbose_name = "Proyecto"

        verbose_name_plural = "Proyectos"

    def __str__(self):

        return self.nombre


class AuditoriaProyecto(models.Model):

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE
    )

    accion = models.CharField(
        max_length=50
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )

    class Meta:

        db_table = "auditoria_proyecto"

    def __str__(self):

        return f"{self.proyecto.nombre} - {self.accion}"
    
class Cronograma(models.Model):

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="cronogramas"
    )

    actividad = models.CharField(
        max_length=200
    )

    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    porcentaje_avance = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        db_table = "cronograma"

        verbose_name = "Cronograma"

        verbose_name_plural = "Cronogramas"

    def __str__(self):

        return self.actividad
    
def save(self, *args, **kwargs):

    if self.estado:

        self.porcentaje_avance = 100

    else:

        self.porcentaje_avance = 0

    super().save(*args, **kwargs)
    
class Documento(models.Model):

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="documentos"
    )

    nombre = models.CharField(
        max_length=150
    )

    descripcion = models.TextField()

    archivo = models.FileField(
        upload_to="documentos/"
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = "documento"

        verbose_name = "Documento"

        verbose_name_plural = "Documentos"

    def __str__(self):

        return self.nombre