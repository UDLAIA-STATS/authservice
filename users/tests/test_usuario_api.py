import pytest
from django.contrib.auth import get_user_model

Usuario = get_user_model()


@pytest.mark.django_db
class TestUsuarioAPI:
    def test_crear_profesor_ok(self, auth_client):
        """Un superusuario puede registrar un profesor"""
        payload = {
            "nombre_usuario": "profe1",
            "email_usuario": "profe1@test.com",
            "contrasenia_usuario": "test123",
            "rol": "profesor"
        }
        response = auth_client.post("/api/register/", payload, format="json")

        assert response.status_code == 201
        assert response.data["usuario"]["rol"] == "profesor"
        assert Usuario.objects.filter(nombre_usuario="profe1").exists()

    def test_no_superuser_no_puede_registrar(self, api_client, profesor):
        """Un profesor no puede registrar otros usuarios"""
        api_client.force_authenticate(user=profesor)
        payload = {
            "nombre_usuario": "nuevo_user",
            "email_usuario": "nuevo@test.com",
            "contrasenia_usuario": "pass"
        }
        response = api_client.post("/api/register/", payload, format="json")
        assert response.status_code == 403

    def test_registro_falla_por_duplicado(self, auth_client):
        """No permite duplicados en nombre o correo"""
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
        response = auth_client.post("/api/register/", payload, format="json")
        assert response.status_code == 400
        assert any(
            key in response.data for key in ("nombre_usuario", "email_usuario", "error")
            )


    # ---------- Login ----------
    def test_login_correcto(self, api_client, superuser):
        """✅ Login devuelve token"""
        response = api_client.post("/api/login/", {
            "nombre_usuario": "admin",
            "contrasenia_usuario": "admin123"
        }, format="json")
        assert response.status_code == 200
        assert "token" in response.data

    def test_login_invalido(self, api_client):
        """Login con credenciales erróneas"""
        response = api_client.post("/api/login/", {
            "nombre_usuario": "admin",
            "contrasenia_usuario": "wrong"
        }, format="json")
        assert response.status_code == 400

    # ---------- Listado ----------
    def test_listar_usuarios_con_paginacion(self, auth_client):
        """Listar usuarios con paginación"""
        for i in range(5):
            Usuario.objects.create_user(
                nombre_usuario=f"user{i}",
                email_usuario=f"user{i}@test.com",
                contrasenia_usuario="abc123"
            )
        response = auth_client.get("/api/users/?page=1&offset=3")
        assert response.status_code == 200
        assert "items" in response.data
        assert "pagination" in response.data
        assert len(response.data["items"]) <= 3

    def test_listar_usuarios_error_parametros(self, auth_client):
        """❌ Parámetros de paginación inválidos"""
        response = auth_client.get("/api/users/?page=0&offset=-1")
        assert response.status_code == 400

    # ---------- Detalle ----------
    def test_detalle_usuario(self, auth_client):
        """Ver detalle de usuario"""
        Usuario.objects.create_user(
            nombre_usuario="detalle",
            email_usuario="detalle@test.com",
            contrasenia_usuario="abc123"
        )
        response = auth_client.get("/api/users/detalle/")
        assert response.status_code == 200
        assert response.data["nombre_usuario"] == "detalle"

    def test_detalle_usuario_no_existe(self, auth_client):
        """Usuario inexistente"""
        response = auth_client.get("/api/users/noexiste/")
        assert response.status_code in (404, 500)

    # ---------- Update ----------
    def test_actualizar_usuario(self, auth_client):
        """Actualiza datos parcialmente"""
        Usuario.objects.create_user(
            nombre_usuario="update_me",
            email_usuario="update@test.com",
            contrasenia_usuario="abc123"
        )
        payload = {"email_usuario": "nuevo_email@test.com"}
        response = auth_client.patch("/api/users/update_me/update/", payload, format="json")
        assert response.status_code == 200
        assert response.data["email_usuario"] == "nuevo_email@test.com"

    def test_actualizar_usuario_inexistente(self, auth_client):
        """❌ Actualización de usuario inexistente"""
        response = auth_client.patch("/api/users/fantasma/update/", {"rol": "profesor"}, format="json")
        assert response.status_code == 404

    # ---------- Delete ----------
    def test_eliminar_usuario(self, auth_client):
        """Elimina usuario correctamente"""
        user = Usuario.objects.create_user(
            nombre_usuario="delete_me",
            email_usuario="delete@test.com",
            contrasenia_usuario="abc123"
        )
        response = auth_client.delete(f"/api/users/{user.nombre_usuario}/delete/")
        assert response.status_code == 204
        assert not Usuario.objects.filter(nombre_usuario="delete_me").exists()

    def test_eliminar_usuario_inexistente(self, auth_client):
        """Intentar eliminar un usuario inexistente"""
        response = auth_client.delete("/api/users/noexiste/delete/")
        assert response.status_code == 404
