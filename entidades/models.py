from django.db import models


class Entidad(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=200
    )

    descripcion = models.TextField()

    responsable = models.CharField(
        max_length=150
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "entidad"
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"

    def __str__(self):
        return self.nombre