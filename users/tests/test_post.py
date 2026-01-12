import json
from venv import logger
from users.tests.config import UsuarioAPITestCase, Usuario


class UsuarioPostTestCase(UsuarioAPITestCase):
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

        # Permite variación en la respuesta; validar con existencia en BD
        self.assertIn(response.status_code, (201, 200))
        self.assertTrue(Usuario.objects.filter(nombre_usuario="profesor").exists())
        self.assertEqual(Usuario.objects.get(nombre_usuario="profesor").rol, "profesor") # type: ignore

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
        ) # type: ignore
        payload = {
            "nombre_usuario": "dup",
            "email_usuario": "dup@udla.edu.ec",
            "contrasenia_usuario": "abc123"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        content_string = response.content.decode('utf-8')
        data = json.loads(content_string)
        self.assertTrue(
            any(k in data for k in ("nombre_usuario", "email_usuario", "error"))
        )
    
    def test_registro_nombre_usuario_minimo_valido(self):
        """Boundary: mínimo de nombre_usuario (válido)"""
        self.auth_as_superuser()
        min_len = 1
        nombre = "a" * min_len
        payload = {
            "nombre_usuario": nombre,
            "email_usuario": f"{nombre}@udla.edu.ec",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertIn(response.status_code, (201, 200))

    def test_registro_nombre_usuario_invalido(self):
        """Boundary: mínimo de nombre_usuario (válido)"""
        self.auth_as_superuser()
        payload = {
            "nombre_usuario": "User 123",
            "email_usuario": f"example@udla.edu.ec",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_registro_nombre_usuario_maximo_valido(self):
        """Boundary: máximo de nombre_usuario (válido)"""
        self.auth_as_superuser()
        max_len = Usuario._meta.get_field('nombre_usuario').max_length
        nombre = "a" * max_len
        payload = {
            "nombre_usuario": nombre,
            "email_usuario": f"{nombre}@udla.edu.ec",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertIn(response.status_code, (201, 200))

    def test_registro_nombre_usuario_fuera_del_maximo(self):
        """Boundary: nombre_usuario excede el máximo"""
        self.auth_as_superuser()
        max_len = Usuario._meta.get_field('nombre_usuario').max_length
        nombre = "a" * (max_len + 1)
        payload = {
            "nombre_usuario": nombre,
            "email_usuario": f"{nombre}@udla.edu.ec",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_registro_email_invalido(self):
        """Boundary: email_usuario inválido"""
        self.auth_as_superuser()
        payload = {
            "nombre_usuario": "testuserdos",
            "email_usuario": "example@gmail.com",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_registro_email_formato_invalido(self):
        """Boundary: formato de email_usuario inválido"""
        self.auth_as_superuser()
        payload = {
            "nombre_usuario": "testusertres",
            "email_usuario": "example@",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_registro_email_maximo_valido(self):
        """Boundary: máximo de email_usuario (válido)"""
        self.auth_as_superuser()
        max_len = Usuario._meta.get_field('email_usuario').max_length
        local_len = max_len - len("@udla.edu.ec")
        local = "a" * (local_len - 1)
        email = f"{local}@udla.edu.ec"
        payload = {
            "nombre_usuario": "testuser",
            "email_usuario": email,
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        content = response.content.decode('utf-8')
        data = json.loads(content)
        self.assertIn(data['status'], (201, 200))
        self.assertEqual(email, data['data']["email_usuario"])

    def test_registro_nombre_usuario_vacio(self):
        """Boundary: nombre_usuario vacío"""
        self.auth_as_superuser()
        payload = {
            "nombre_usuario": "",
            "email_usuario": "empty@udla.edu.ec",
            "contrasenia_usuario": "test1234",
            "rol": "profesor"
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 400)

