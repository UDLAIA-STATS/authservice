from django.test import TestCase

# Create your tests here.
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

Usuario = get_user_model()

@pytest.mark.django_db
class TestUsuarioAPI:
    def setup_method(self):
        self.client = APIClient()
        # Crear superusuario
        self.superuser = Usuario.objects.create_superuser(
            nombre_usuario='admin',
            email_usuario='admin@test.com',
            contrasenia_usuario='admin123'
        )
        self.client.force_authenticate(user=self.superuser)

    def test_crear_profesor(self):
        """✅ Verifica que un superusuario pueda registrar un profesor"""
        response = self.client.post('/registro/', {
            'nombre_usuario': 'profesor1',
            'email_usuario': 'profe1@test.com',
            'contrasenia_usuario': 'test123',
            'rol': 'profesor'
        }, format='json')

        assert response.status_code == 201
        assert response.data['usuario']['rol'] == 'profesor'

    def test_no_superuser_no_puede_crear(self):
        """❌ Verifica que un profesor no pueda registrar otros usuarios"""
        # Autenticar como profesor
        profe = Usuario.objects.create_user(
            nombre_usuario='profe2',
            email_usuario='profe2@test.com',
            contrasenia_usuario='123456',
            rol='profesor'
        )
        self.client.force_authenticate(user=profe)

        response = self.client.post('/registro/', {
            'nombre_usuario': 'nuevo_user',
            'email_usuario': 'nuevo@test.com',
            'contrasenia_usuario': 'pass'
        }, format='json')

        assert response.status_code == 403  # Forbidden

    def test_login_funciona(self):
        """✅ Verifica login correcto"""
        client = APIClient()
        response = client.post('/login/', {
            'nombre_usuario': 'admin',
            'contrasenia_usuario': 'admin123'
        }, format='json')

        assert response.status_code == 200
        assert 'token' in response.data
