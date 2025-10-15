from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from .serializers import RegistroUsuarioSerializer, LoginUsuarioSerializer


class EsSuperUsuario(permissions.BasePermission):
    """Permiso: solo los superusuarios pueden acceder"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class RegistroUsuarioView(APIView):
    """
    Solo los superusuarios pueden registrar nuevos usuarios (profesores o superusuarios).
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'mensaje': 'Usuario creado exitosamente',
                    'usuario': {
                        'id': user.id,
                        'nombre_usuario': user.nombre_usuario,
                        'email_usuario': user.email_usuario,
                        'rol': user.rol
                    },
                    'token': token.key
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'error': 'El usuario o correo ya están registrados.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUsuarioView(APIView):
    """
    Permite que profesores y superusuarios inicien sesión.
    Devuelve el token y los datos del usuario.
    """
    def post(self, request):
        serializer = LoginUsuarioSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'usuario': {
                    'id': user.id,
                    'nombre_usuario': user.nombre_usuario,
                    'email_usuario': user.email_usuario,
                    'rol': user.rol
                },
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
