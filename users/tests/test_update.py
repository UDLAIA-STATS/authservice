import json
from users.tests.config import Usuario, UsuarioAPITestCase


class UsuarioUpdateTestCase(UsuarioAPITestCase):
    def test_actualizar_usuario(self):
        """✅ Actualiza datos parcialmente"""
        self.auth_as_superuser()
        Usuario.objects.create_user(
            nombre_usuario="update me",
            email_usuario="update@udla.edu.ec",
            contrasenia_usuario="abc123"
        ) # type: ignore
        payload = {"email_usuario": "nuevo_email@udla.edu.ec"}
        response = self.client.patch("/api/users/update me/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)

        content_string = response.content.decode('utf-8')
        data = json.loads(content_string)

        self.assertEqual(data['data']["email_usuario"], "nuevo_email@udla.edu.ec")

    def test_actualizar_usuario_inexistente(self):
        """❌ Actualización de usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.patch("/api/users/fantasma/update/", {"rol": "profesor"}, format="json")
        self.assertEqual(response.status_code, 404)
