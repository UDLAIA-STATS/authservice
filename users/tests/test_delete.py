from users.tests.config import UsuarioAPITestCase, Usuario


class UsuarioDeleteTestCase(UsuarioAPITestCase):
    def test_eliminar_usuario(self):
        """
        Verificar que se puede eliminar un usuario exitosamente.
        """

        self.auth_as_superuser()
        user = Usuario.objects.create_user(
            nombre_usuario="delete me",
            email_usuario="delete@udla.edu.ec",
            contrasenia_usuario="abc123"
        )  # type: ignore
        response = self.client.delete(f"/api/users/{user.nombre_usuario}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(nombre_usuario="delete me").first().is_active)

    def test_eliminar_usuario_inexistente(self):
        """
        Verificar que se devuelve un error 404 al intentar eliminar un usuario inexistente.
        """
        self.auth_as_superuser()
        response = self.client.delete("/api/users/noexiste/delete/")
        self.assertEqual(response.status_code, 404)
