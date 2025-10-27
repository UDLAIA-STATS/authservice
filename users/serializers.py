from rest_framework import serializers
from django.db import IntegrityError
from .models import Usuario
from django.contrib.auth import authenticate

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    contrasenia_usuario = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_usuario', 'email_usuario', 'contrasenia_usuario', 'rol']
        read_only_fields = ['id']

    def create(self, validated_data):
        try:
            user = Usuario.objects.create_user(
                nombre_usuario=validated_data['nombre_usuario'],
                email_usuario=validated_data['email_usuario'],
                contrasenia_usuario=validated_data['contrasenia_usuario'],
                rol=validated_data.get('rol', 'profesor')
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({'error': str(e)})
        except IntegrityError:
            raise serializers.ValidationError({'error': 'El usuario o correo ya está registrado.'})
        
    def update(self, instance, validated_data):
        if 'nombre_usuario' in validated_data:
            instance.nombre_usuario = validated_data.get('nombre_usuario', instance.nombre_usuario)
        if 'email_usuario' in validated_data:
            instance.email_usuario = validated_data.get('email_usuario', instance.email_usuario)
        if 'contrasenia_usuario' in validated_data:
            password = validated_data['contrasenia_usuario']
            if password:
                instance.set_password(password)
        instance.rol = validated_data.get('rol', instance.rol)
        instance.save()
        return instance
    
    def delete(self, instance):
        instance.delete()
        return instance


class LoginUsuarioSerializer(serializers.Serializer):
    nombre_usuario = serializers.CharField()
    contrasenia_usuario = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            request=self.context.get('request'),
            username=data['nombre_usuario'],
            password=data['contrasenia_usuario']
        )
        if not user:
            raise serializers.ValidationError("Usuario o contraseña incorrecta")
        if not user.is_active:
            raise serializers.ValidationError("La cuenta está desactivada")
        return user
