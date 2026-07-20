from django.test import TestCase
from django.urls import reverse

class UsuarioTest(TestCase):

    def test_login_page(self):

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)