import re
from rest_framework import serializers
from django.db import IntegrityError
from .models import Usuario
from django.contrib.auth import authenticate

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    contrasenia_usuario = serializers.CharField(write_only=True)


    class Meta:
        model = Usuario
        fields = ['id', 'nombre_usuario', 'email_usuario', 'contrasenia_usuario', 'rol', 'is_active']
        read_only_fields = ['id']

    def create(self, validated_data):
        try:
            user = Usuario.objects.create_user( # type: ignore
                nombre_usuario=validated_data['nombre_usuario'],
                email_usuario=validated_data['email_usuario'],
                contrasenia_usuario=validated_data['contrasenia_usuario'],
                rol=validated_data.get('rol', 'profesor'),
                is_active=validated_data.get('is_active', True)
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({'error': str(e)})
        except IntegrityError:
            raise serializers.ValidationError({'error': 'El usuario o correo ya está registrado.'})
        
    def update(self, instance, validated_data):
        instance.nombre_usuario = validated_data.get('nombre_usuario', instance.nombre_usuario)
        instance.email_usuario = validated_data.get('email_usuario', instance.email_usuario)
        if 'contrasenia_usuario' in validated_data:
            password = validated_data['contrasenia_usuario']
            if password:
                instance.set_password(password)
        instance.rol = validated_data.get('rol', instance.rol)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance
    
    def delete(self, instance):
        if not instance.is_active:
            raise serializers.ValidationError("El usuario ya está desactivado.")
        instance.is_active = False
        instance.save()
        return instance
    
    def validate_nombre_usuario(self, value):
        patron = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ ]+$"
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de usuario no puede estar vacío.")
        if not re.match(patron, value):
            raise serializers.ValidationError("El nombre de usuario debe contener solo letras y espacios.")
        if value.lower().strip() == 'admin':
            raise serializers.ValidationError("El nombre de usuario 'admin' no está permitido.")
        if Usuario.objects.filter(nombre_usuario=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        
        return value

    def validate_email_usuario(self, value):
        patron = r'^[a-zA-Z0-9._%+-]+@udla\.edu\.ec$'
        if not value or not value.strip():
            raise serializers.ValidationError("El correo electrónico no puede estar vacío.")

        value = value.lower()

        if not re.match(patron, value):
            raise serializers.ValidationError("El correo electrónico debe pertenecer al dominio udla.edu.ec.")

        if Usuario.objects.filter(email_usuario=value).exists():
            raise serializers.ValidationError("El correo electrónico ya está en uso.")
        
        return value


class LoginUsuarioSerializer(serializers.Serializer):
    nombre_usuario = serializers.CharField()
    contrasenia_usuario = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['nombre_usuario'],
            password=attrs['contrasenia_usuario']
        )
        if not user:
            raise serializers.ValidationError("Usuario o contraseña incorrecta", code='authorization')
        if not user.is_active:
            raise serializers.ValidationError("La cuenta está desactivada", code='authorization')
        return user
