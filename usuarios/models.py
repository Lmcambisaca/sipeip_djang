from django.db import models
from django.contrib.auth.models import AbstractUser

from roles.models import Rol


class Usuario(AbstractUser):

    email = models.EmailField(
        unique=True
    )

    estado = models.BooleanField(
        default=True
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios"
    )

    # TAR-33
    intentos_fallidos = models.PositiveIntegerField(
        default=0
    )

    bloqueado = models.BooleanField(
        default=False
    )

    class Meta:

        db_table = "usuario"

        verbose_name = "Usuario"

        verbose_name_plural = "Usuarios"

    def __str__(self):

        return self.get_full_name() or self.username
    
class RecuperacionPassword(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="recuperaciones"
    )

    fecha_solicitud = models.DateTimeField(
        auto_now_add=True
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        db_table = "recuperacion_password"

        verbose_name = "Recuperación de contraseña"

        verbose_name_plural = "Recuperaciones de contraseña"


    def __str__(self):

        return self.usuario.email
    
class AuditoriaSesion(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="auditorias"
    )

    accion = models.CharField(
        max_length=30
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = "auditoria_sesion"

        verbose_name = "Auditoría de sesión"

        verbose_name_plural = "Auditorías de sesión"

    def __str__(self):

        return f"{self.usuario.username} - {self.accion}"