import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

Usuario = get_user_model()

@pytest.fixture
def api_client():
    """Cliente API genérico de DRF."""
    return APIClient()

@pytest.fixture
def superuser(db):
    """Crea y retorna un superusuario autenticado."""
    user = Usuario.objects.create_superuser(
        nombre_usuario="admin",
        email_usuario="admin@test.com",
        contrasenia_usuario="admin123"
    )
    Token.objects.get_or_create(user=user)
    return user

@pytest.fixture
def profesor(db):
    """Crea y retorna un usuario tipo profesor."""
    return Usuario.objects.create_user(
        nombre_usuario="profe",
        email_usuario="profe@test.com",
        contrasenia_usuario="123456",
        rol="profesor"
    )

@pytest.fixture
def auth_client(api_client, superuser):
    """Cliente autenticado como superusuario."""
    api_client.force_authenticate(user=superuser)
    return api_client
