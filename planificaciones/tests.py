from django.test import TestCase


class PlanificacionTest(TestCase):

    def test_respuesta_consultar(self):

        response = self.client.get("/planificaciones/consultar/")

        self.assertIn(

            response.status_code,

            [200,302]

        )