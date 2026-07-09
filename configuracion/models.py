from django.db import models


class Configuracion(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    valor = models.CharField(
        max_length=255
    )

    descripcion = models.TextField()

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        db_table = "configuracion"

        verbose_name = "Configuración"

        verbose_name_plural = "Configuraciones"

    def __str__(self):

        return self.nombre