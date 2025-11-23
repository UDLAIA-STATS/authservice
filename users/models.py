#Models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, email_usuario, contrasenia_usuario=None, **extra_fields):
        if not email_usuario:
            raise ValueError('El email es obligatorio')

        email_usuario = self.normalize_email(email_usuario)

        # ⚠️ Validaciones por duplicados
        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            raise ValueError('Ya existe un usuario con ese nombre de usuario')
        if Usuario.objects.filter(email_usuario=email_usuario).exists():
            raise ValueError('Ya existe un usuario con ese correo electrónico')

        user = self.model(
            nombre_usuario=nombre_usuario,
            email_usuario=email_usuario,
            **extra_fields
        )
        user.set_password(contrasenia_usuario)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, email_usuario, contrasenia_usuario=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'superuser')
        password = contrasenia_usuario
        if not password:
            # Default password that should be changed by the user on first login
            password = 'admin123'
        return self.create_user(nombre_usuario, email_usuario, password, **extra_fields)
    

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('superuser', 'Superusuario'),
        ('profesor', 'Profesor'),
    )

    nombre_usuario = models.CharField(max_length=50, unique=True)
    email_usuario = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='profesor')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email_usuario']

    def __str__(self):
        return f"{self.nombre_usuario} ({self.rol})"
    
    class Meta:
        db_table = 'usuarios'
