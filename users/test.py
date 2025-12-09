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
            email_usuario="admin@udla.edu.ec",
            contrasenia_usuario="admin123"
        )
        Token.objects.get_or_create(user=self.superuser)

        self.profesor = Usuario.objects.create_user(
            nombre_usuario="profe",
            email_usuario="profe@udla.edu.ec",
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
            "nombre_usuario": "profesor",
            "email_usuario": "profesor@udla.edu.ec",
            "contrasenia_usuario": "test123",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["usuario"]["rol"], "profesor")
        self.assertTrue(Usuario.objects.filter(nombre_usuario="profesor").exists())

    def test_no_superuser_no_puede_registrar(self):
        """❌ Un profesor no puede registrar otros usuarios"""
        self.auth_as_profesor()
        payload = {
            "nombre_usuario": "nuevo user",
            "email_usuario": "nuevo@udla.edu.ec",
            "contrasenia_usuario": "pass"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_registro_falla_por_duplicado(self):
        """❌ No permite duplicados en nombre o correo"""
        self.auth_as_superuser()
        Usuario.objects.create_user(
            nombre_usuario="dup",
            email_usuario="dup@udla.edu.ec",
            contrasenia_usuario="abc123"
        )
        payload = {
            "nombre_usuario": "dup",
            "email_usuario": "dup@udla.edu.ec",
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
        names = ["Johana", "Carlos", "Ana", "Luis", "María"]
        for i in range(5):
            Usuario.objects.create_user(
                nombre_usuario=f"{names[i]}",
                email_usuario=f"user{i}@udla.edu.ec",
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
            email_usuario="detalle@udla.edu.ec",
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
            nombre_usuario="update me",
            email_usuario="update@udla.edu.ec",
            contrasenia_usuario="abc123"
        )
        payload = {"email_usuario": "nuevo_email@udla.edu.ec"}
        response = self.client.patch("/api/users/update me/update/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email_usuario"], "nuevo_email@udla.edu.ec")

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
            nombre_usuario="delete me",
            email_usuario="delete@udla.edu.ec",
            contrasenia_usuario="abc123"
        )
        response = self.client.delete(f"/api/users/{user.nombre_usuario}/delete/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Usuario.objects.filter(nombre_usuario="delete me").first().is_active)

    def test_eliminar_usuario_inexistente(self):
        """❌ Intentar eliminar un usuario inexistente"""
        self.auth_as_superuser()
        response = self.client.delete("/api/users/noexiste/delete/")
        self.assertEqual(response.status_code, 404)

    # ---------- Health ----------
    def test_health_endpoint_returns_200(self):
        """✅ El endpoint /health/ retorna 200 OK"""
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint_returns_json_with_status_ok(self):
        """✅ El endpoint /health/ retorna JSON con {"status": "ok"}"""
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})

    def test_health_endpoint_allows_access_without_authentication(self):
        """✅ El endpoint /health/ permite acceso sin autenticación"""
        # No autenticamos al cliente
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})
