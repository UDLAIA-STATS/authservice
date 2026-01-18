from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


Usuario = get_user_model()

class UsuarioAPITestCase(TestCase):
    """Pruebas funcionales para el API de usuarios utilizando TestCase de Django."""

    def setUp(self):
        """Configuración inicial: cliente API y usuarios base."""
        self.client = APIClient()

        self.superuser = Usuario.objects.create_superuser(
            nombre_usuario="admin",
            email_usuario="admin@udla.edu.ec",
            contrasenia_usuario="admin123"
        ) # type: ignore
        Token.objects.get_or_create(user=self.superuser)

        self.profesor = Usuario.objects.create_user(
            nombre_usuario="profe",
            email_usuario="profe@udla.edu.ec",
            contrasenia_usuario="123456",
            rol="profesor"
        ) # type: ignore

    def _payload(self, response):
        data = getattr(response, "data", None)
        if isinstance(data, dict) and isinstance(data.get("data"), dict):
            return data["data"]
        return data or {}

    def _get_field(self, payload, *keys):
        cur = payload
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return None
        return cur
    
    def auth_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)

    def auth_as_profesor(self):
        self.client.force_authenticate(user=self.profesor)
