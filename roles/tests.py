from django.test import TestCase

from .models import Rol, Permiso


class RolPermisoTest(TestCase):

    def test_crear_rol(self):

        rol = Rol.objects.create(
            nombre="Rol de Prueba",
            descripcion="Rol creado para pruebas"
        )

        self.assertEqual(
            rol.nombre,
            "Rol de Prueba"
        )

    def test_asignar_permiso_a_rol(self):

        rol = Rol.objects.create(
            nombre="Administrador de Prueba",
            descripcion="Rol para pruebas"
        )

        permiso = Permiso.objects.create(
            nombre="Permiso de Prueba",
            descripcion="Permiso creado para pruebas"
        )

        rol.permisos.add(permiso)

        self.assertTrue(
            rol.permisos.filter(
                id=permiso.id
            ).exists()
        )