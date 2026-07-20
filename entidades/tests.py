from django.test import TestCase

from .models import Entidad


class EntidadTest(TestCase):

    def test_crear_entidad(self):

        entidad = Entidad.objects.create(

            nombre="Entidad Prueba",

            descripcion="Entidad para pruebas"

        )

        self.assertEqual(

            entidad.nombre,

            "Entidad Prueba"

        )