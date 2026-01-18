from users.tests.config import UsuarioAPITestCase, Usuario


class UsuarioDeleteTestCase(UsuarioAPITestCase):
    def test_eliminar_usuario(self):
        """✅ Elimina usuario correctamente"""
        self.auth_as_superuser()
        user = Usuario.objects.create_user(
            nombre_usuario="delete me",
            email_usuario="delete@udla.edu.ec",
            contrasenia_usuario="abc123"
        ) # type: ignore
        response = self.client.delete(f"/api/users/{user.nombre_usuario}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(nombre_usuario="delete me").first().is_active)

    def test_eliminar_usuario_inexistente(self):
        """❌ Intentar eliminar un usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.delete("/api/users/noexiste/delete/")
        self.assertEqual(response.status_code, 404)
