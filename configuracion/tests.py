from django.test import TestCase

from .models import Configuracion


class ConfiguracionTest(TestCase):

    def test_crear_configuracion(self):

        configuracion = Configuracion.objects.create(
            nombre="Parámetro de Prueba",
            valor="Valor de Prueba",
            descripcion="Configuración creada para pruebas"
        )

        self.assertEqual(
            configuracion.nombre,
            "Parámetro de Prueba"
        )

        self.assertTrue(
            configuracion.estado
        )