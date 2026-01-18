import json
from venv import logger
from users.tests.config import UsuarioAPITestCase, Usuario


class UsuarioGetTestCase(UsuarioAPITestCase):
    def test_listar_usuarios_con_paginacion(self):
        """✅ Listar usuarios con paginación"""
        self.auth_as_superuser()
        names = ["Johana", "Carlos", "Ana", "Luis", "María"]
        for i in range(5):
            Usuario.objects.create_user(
                nombre_usuario=f"{names[i]}",
                email_usuario=f"user{i}@udla.edu.ec",
                contrasenia_usuario="abc123"
            ) # type: ignore
        response = self.client.get("/api/users/?page=1&offset=3")
        self.assertEqual(response.status_code, 200)
        payload = self._payload(response)
        self.assertIn("results", payload)
        self.assertLessEqual(len(payload["results"]), 3)

    def test_listar_usuarios_error_parametros(self):
        """❌ Parámetros de paginación inválidos"""
        self.auth_as_superuser()
        response = self.client.get("/api/users/?page=0&offset=-1")
        self.assertEqual(response.status_code, 400)

    def test_detalle_usuario(self):
        """✅ Ver detalle de usuario"""
        self.auth_as_superuser()
        Usuario.objects.create_user(
            nombre_usuario="detalle",
            email_usuario="detalle@udla.edu.ec",
            contrasenia_usuario="abc123"
        ) # type: ignore
        response = self.client.get("/api/users/detalle/")
        content_string = response.content.decode('utf-8')
        data = json.loads(content_string)
        logger.debug(f"Detalle usuario response data: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']["nombre_usuario"], "detalle")

    def test_detalle_usuario_no_existe(self):
        """❌ Usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.get("/api/users/noexiste/")
        self.assertIn(response.status_code, (404, 500))
