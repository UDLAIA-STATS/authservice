from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario

# Serializer para registro de usuario
class RegistroUsuarioSerializer(serializers.ModelSerializer):
    contrasenia_usuario = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'email_usuario', 'contrasenia_usuario']

    def create(self, validated_data):
        # Crear usuario usando el manager correctamente
        user = Usuario.objects.create_user(
            nombre_usuario=validated_data['nombre_usuario'],
            email_usuario=validated_data['email_usuario'],
            contrasenia_usuario=validated_data['contrasenia_usuario']
        )
        return user

# Serializer para login de usuario
class LoginUsuarioSerializer(serializers.Serializer):
    nombre_usuario = serializers.CharField()
    contrasenia_usuario = serializers.CharField(write_only=True)

    def validate(self, data):
        # Autenticar usando el método authenticate
        user = authenticate(
            request=self.context.get('request'),  # contexto opcional
            username=data['nombre_usuario'], 
            password=data['contrasenia_usuario']
        )
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        return user
