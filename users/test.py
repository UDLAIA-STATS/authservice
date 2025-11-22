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
        # Crear superusuario y token
        self.superuser = Usuario.objects.create_superuser(
            nombre_usuario="admin",
            email_usuario="admin@test.com",
            contrasenia_usuario="admin123"
        )
        Token.objects.get_or_create(user=self.superuser)

        self.profesor = Usuario.objects.create_user(
            nombre_usuario="profe",
            email_usuario="profe@test.com",
            contrasenia_usuario="123456",
            rol="profesor"
        )

    # ---------- Helpers ----------
    def auth_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)

    def auth_as_profesor(self):
        self.client.force_authenticate(user=self.profesor)

    # ---------- Registro ----------
    def test_crear_profesor_ok(self):
        """✅ Un superusuario puede registrar un profesor"""
        self.auth_as_superuser()
        payload = {
            "nombre_usuario": "profe1",
            "email_usuario": "profe1@test.com",
            "contrasenia_usuario": "test123",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["usuario"]["rol"], "profesor")
        self.assertTrue(Usuario.objects.filter(nombre_usuario="profe1").exists())

    def test_no_superuser_no_puede_registrar(self):
        """❌ Un profesor no puede registrar otros usuarios"""
        self.auth_as_profesor()
        payload = {
            "nombre_usuario": "nuevo_user",
            "email_usuario": "nuevo@test.com",
            "contrasenia_usuario": "pass"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_registro_falla_por_duplicado(self):
        """❌ No permite duplicados en nombre o correo"""
        self.auth_as_superuser()
        Usuario.objects.create_user(
            nombre_usuario="dup",
            email_usuario="dup@test.com",
            contrasenia_usuario="abc123"
        )
        payload = {
            "nombre_usuario": "dup",
            "email_usuario": "dup@test.com",
            "contrasenia_usuario": "abc123"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            any(k in response.data for k in ("nombre_usuario", "email_usuario", "error"))
        )

    # ---------- Login ----------
    def test_login_correcto(self):
        """✅ Login devuelve token"""
        response = self.client.post("/api/login/", {
            "nombre_usuario": "admin",
            "contrasenia_usuario": "admin123"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_login_invalido(self):
        """❌ Login con credenciales erróneas"""
        response = self.client.post("/api/login/", {
            "nombre_usuario": "admin",
            "contrasenia_usuario": "wrong"
        }, format="json")
        self.assertEqual(response.status_code, 400)

    # ---------- Listado ----------
    def test_listar_usuarios_con_paginacion(self):
        """✅ Listar usuarios con paginación"""
        self.auth_as_superuser()
        for i in range(5):
            Usuario.objects.create_user(
                nombre_usuario=f"user{i}",
                email_usuario=f"user{i}@test.com",
                contrasenia_usuario="abc123"
            )
        response = self.client.get("/api/users/?page=1&offset=3")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.data)
        self.assertIn("pagination", response.data)
        self.assertLessEqual(len(response.data["items"]), 3)

    def test_listar_usuarios_error_parametros(self):
        """❌ Parámetros de paginación inválidos"""
        self.auth_as_superuser()
        response = self.client.get("/api/users/?page=0&offset=-1")
        self.assertEqual(response.status_code, 400)

    # ---------- Detalle ----------
    def test_detalle_usuario(self):
        """✅ Ver detalle de usuario"""
        self.auth_as_superuser()
        Usuario.objects.create_user(
            nombre_usuario="detalle",
            email_usuario="detalle@test.com",
            contrasenia_usuario="abc123"
        )
        response = self.client.get("/api/users/detalle/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nombre_usuario"], "detalle")

    def test_detalle_usuario_no_existe(self):
        """❌ Usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.get("/api/users/noexiste/")
        self.assertIn(response.status_code, (404, 500))

    # ---------- Update ----------
    def test_actualizar_usuario(self):
        """✅ Actualiza datos parcialmente"""
        self.auth_as_superuser()
        Usuario.objects.create_user(
            nombre_usuario="update_me",
            email_usuario="update@test.com",
            contrasenia_usuario="abc123"
        )
        payload = {"email_usuario": "nuevo_email@test.com"}
        response = self.client.patch("/api/users/update_me/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email_usuario"], "nuevo_email@test.com")

    def test_actualizar_usuario_inexistente(self):
        """❌ Actualización de usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.patch("/api/users/fantasma/update/", {"rol": "profesor"}, format="json")
        self.assertEqual(response.status_code, 404)

    # ---------- Delete ----------
    def test_eliminar_usuario(self):
        """✅ Elimina usuario correctamente"""
        self.auth_as_superuser()
        user = Usuario.objects.create_user(
            nombre_usuario="delete_me",
            email_usuario="delete@test.com",
            contrasenia_usuario="abc123"
        )
        response = self.client.delete(f"/api/users/{user.nombre_usuario}/delete/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Usuario.objects.filter(nombre_usuario="delete_me").first().is_active)

    def test_eliminar_usuario_inexistente(self):
        """❌ Intentar eliminar un usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.delete("/api/users/noexiste/delete/")
        self.assertEqual(response.status_code, 404)
