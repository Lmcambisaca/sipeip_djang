from django.test import TestCase


class ProyectoTest(TestCase):

    def test_consulta(self):

        response = self.client.get("/proyectos/consultar/")

        self.assertIn(

            response.status_code,

            [200,302]

        )