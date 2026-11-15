from django.test import TestCase

from .models import ObjetivoDesarrollo


class ObjetivoDesarrolloTest(TestCase):

    def test_crear_objetivo_desarrollo(self):

        objetivo = ObjetivoDesarrollo.objects.create(
            codigo="ODS-TEST-01",
            descripcion="Objetivo creado para pruebas",
            eje_estrategico="Eje de prueba",
            periodo_vigencia="2026-2030"
        )

        self.assertEqual(
            objetivo.codigo,
            "ODS-TEST-01"
        )