from django.db import models
from django.contrib.auth.models import AbstractUser
from roles.models import Rol


class Usuario(AbstractUser):

    email = models.EmailField(unique=True)

    estado = models.BooleanField(default=True)

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios"
    )

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name()