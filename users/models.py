from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, email_usuario, contrasenia_usuario=None):
        if not email_usuario:
            raise ValueError("No existe el correo de usuario o no es valido")
        
        email_usuario = self.normalize_email(email_usuario)
        user = self.model(nombre_usuario=nombre_usuario, email_usuario=email_usuario)
        user.set_password(contrasenia_usuario)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, nombre_usuario, email_usuario, contrasenia_usuario=None):
        user = self.create_user(nombre_usuario, email_usuario, contrasenia_usuario)
        user.is_admin = True
        user.save(using=self._db)
        return user
    
class Usuario(AbstractBaseUser):
    nombre_usuario = models.CharField(max_length=50, unique=True)
    email_usuario = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email_usuario']
    
    def __str__(self):
        return str(self.nombre_usuario)
    
    @property
    def is_staff(self):
        return self.is_admin
