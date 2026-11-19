from django.db import models
from django.contrib.auth.models import AbstractUser

from roles.models import Rol
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder


class Usuario(AbstractUser):

    email = models.EmailField(
        unique=True
    )

    identificacion = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    cargo = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    entidad = models.ForeignKey(
        "entidades.Entidad",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
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

class AuditoriaSesionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError(
            "Los registros de auditoría no se pueden modificar."
        )

    def delete(self):
        raise ValidationError(
            "Los registros de auditoría no se pueden eliminar."
        )

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError(
            "Los registros de auditoría no se pueden modificar."
        )


class AuditoriaSesionManager(
    models.Manager.from_queryset(AuditoriaSesionQuerySet)
):
    pass


class AuditoriaSesion(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="auditorias",
    )
    modulo = models.CharField(
        max_length=100,
        default="Sistema",
    )
    accion = models.CharField(
        max_length=100,
    )
    descripcion = models.TextField(
        blank=True,
        default="",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
    )

    objects = AuditoriaSesionManager()

    class Meta:
        db_table = "auditoria_sesion"
        verbose_name = "Auditoría del sistema"
        verbose_name_plural = "Auditorías del sistema"
        ordering = ["-fecha", "-pk"]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError(
                "Los registros de auditoría no se pueden modificar."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Los registros de auditoría no se pueden eliminar."
        )

    def __str__(self):
        return f"{self.usuario.username} - {self.modulo} - {self.accion}"

class HistorialCambioQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError(
            "El historial de cambios no se puede modificar."
        )

    def delete(self):
        raise ValidationError(
            "El historial de cambios no se puede eliminar."
        )

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError(
            "El historial de cambios no se puede modificar."
        )


class HistorialCambioManager(
    models.Manager.from_queryset(HistorialCambioQuerySet)
):
    pass


class HistorialCambio(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="historial_cambios",
    )
    modulo = models.CharField(max_length=100)
    entidad = models.CharField(max_length=100)
    registro_id = models.CharField(max_length=100)
    accion = models.CharField(max_length=100, default="Actualización")
    valores_anteriores = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
    )
    valores_nuevos = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
    )
    fecha = models.DateTimeField(auto_now_add=True)

    objects = HistorialCambioManager()

    class Meta:
        db_table = "historial_cambio"
        verbose_name = "Historial de cambio"
        verbose_name_plural = "Historial de cambios"
        ordering = ["-fecha", "-pk"]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError(
                "El historial de cambios no se puede modificar."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "El historial de cambios no se puede eliminar."
        )

    def __str__(self):
        return f"{self.modulo} - {self.entidad} #{self.registro_id}"