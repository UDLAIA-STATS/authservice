from django.test import TestCase
from users.models import Usuario
from users.serializers import (
    RegistroUsuarioSerializer,
    ActualizarUsuarioSerializer,
    LoginUsuarioSerializer,
)


class RegistroUsuarioSerializerTest(TestCase):
    def test_create_serializer(self):
        serializer = RegistroUsuarioSerializer(
            data={
                "nombre_usuario": "Juan Perez",
                "email_usuario": "juan@udla.edu.ec",
                "contrasenia_usuario": "123456",
                "rol": "profesor",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()

        self.assertTrue(usuario.check_password("123456"))
        self.assertEqual(usuario.rol, "profesor")

    def test_update_serializer(self):
        usuario = Usuario.objects.create_user(
            nombre_usuario="Juan",
            email_usuario="juan@udla.edu.ec",
            contrasenia_usuario="123456",
        )

        serializer = RegistroUsuarioSerializer(
            usuario,
            data={
                "nombre_usuario": "Pedro",
                "email_usuario": "pedro@udla.edu.ec",
                "contrasenia_usuario": "654321",
                "rol": "superuser",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        usuario = serializer.save()

        self.assertEqual(usuario.nombre_usuario, "Pedro")
        self.assertEqual(usuario.email_usuario, "pedro@udla.edu.ec")
        self.assertEqual(usuario.rol, "superuser")
        self.assertTrue(usuario.check_password("654321"))

    def test_delete_serializer(self):
        usuario = Usuario.objects.create_user(
            nombre_usuario="Juan",
            email_usuario="juan@udla.edu.ec",
            contrasenia_usuario="123456",
        )

        serializer = RegistroUsuarioSerializer()

        serializer.delete(usuario)

        usuario.refresh_from_db()

        self.assertFalse(usuario.is_active)

    def test_delete_usuario_ya_desactivado(self):
        usuario = Usuario.objects.create_user(
            nombre_usuario="Juan",
            email_usuario="juan@udla.edu.ec",
            contrasenia_usuario="123456",
            is_active=False,
        )

        serializer = RegistroUsuarioSerializer()

        with self.assertRaisesMessage(
            Exception,
            "El usuario ya está desactivado."
        ):
            serializer.delete(usuario)


class ActualizarUsuarioSerializerTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            nombre_usuario="Juan",
            email_usuario="juan@udla.edu.ec",
            contrasenia_usuario="123456",
        )

    def test_update_password(self):
        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"contrasenia_usuario": "abcdef"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        usuario = serializer.save()

        self.assertTrue(usuario.check_password("abcdef"))

    def test_update_sin_password(self):
        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"rol": "superuser"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        usuario = serializer.save()

        self.assertEqual(usuario.rol, "superuser")

    def test_nombre_admin_no_permitido(self):
        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"nombre_usuario": "admin"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("nombre_usuario", serializer.errors)

    def test_nombre_con_numeros(self):
        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"nombre_usuario": "Juan123"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())

    def test_nombre_vacio(self):
        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"nombre_usuario": "   "},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())

    def test_email_fuera_de_udla(self):
        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"email_usuario": "gmail@gmail.com"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())

    def test_email_duplicado(self):
        Usuario.objects.create_user(
            nombre_usuario="Pedro",
            email_usuario="pedro@udla.edu.ec",
            contrasenia_usuario="123456",
        )

        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"email_usuario": "pedro@udla.edu.ec"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())

    def test_nombre_duplicado(self):
        Usuario.objects.create_user(
            nombre_usuario="Pedro",
            email_usuario="pedro2@udla.edu.ec",
            contrasenia_usuario="123456",
        )

        serializer = ActualizarUsuarioSerializer(
            self.usuario,
            data={"nombre_usuario": "Pedro"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())


class LoginUsuarioSerializerTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            nombre_usuario="Juan",
            email_usuario="juan@udla.edu.ec",
            contrasenia_usuario="123456",
        )

    def test_login_serializer_valido(self):
        serializer = LoginUsuarioSerializer(
            data={
                "nombre_usuario": "Juan",
                "contrasenia_usuario": "123456",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_login_password_incorrecta(self):
        serializer = LoginUsuarioSerializer(
            data={
                "nombre_usuario": "Juan",
                "contrasenia_usuario": "xxxx",
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_login_usuario_inactivo(self):
        self.usuario.is_active = False
        self.usuario.save()

        serializer = LoginUsuarioSerializer(
            data={
                "nombre_usuario": "Juan",
                "contrasenia_usuario": "123456",
            }
        )

        self.assertFalse(serializer.is_valid())