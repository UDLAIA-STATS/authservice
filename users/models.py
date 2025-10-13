from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, email_usuario, contrasenia_usuario=None, **extra_fields):
        if not email_usuario:
            raise ValueError('El email es obligatorio')
        email_usuario = self.normalize_email(email_usuario)
        user = self.model(nombre_usuario=nombre_usuario, email_usuario=email_usuario, **extra_fields)
        user.set_password(contrasenia_usuario)  # ⚡ Muy importante
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, email_usuario, contrasenia_usuario=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nombre_usuario, email_usuario, contrasenia_usuario, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre_usuario = models.CharField(max_length=50, unique=True)
    email_usuario = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email_usuario']

    def __str__(self):
        return str(self.nombre_usuario)
    
