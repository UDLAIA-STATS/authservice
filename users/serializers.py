from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    contrasenia_usuario = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'email_usuario', 'contrasenia_usuario']

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            nombre_usuario=validated_data['nombre_usuario'],
            email_usuario=validated_data['email_usuario'],
            contrasenia_usuario=validated_data['contrasenia_usuario']
        )
        return user


class LoginUsuarioSerializer(serializers.Serializer):
    nombre_usuario = serializers.CharField()
    contrasenia_usuario = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            request=self.context.get('request'),
            username=data['nombre_usuario'],  # debe coincidir con USERNAME_FIELD
            password=data['contrasenia_usuario']
        )
        if not user:
            raise serializers.ValidationError("Usuario o contraseña incorrecta")
        return user
