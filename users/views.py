from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from .serializers import RegistroUsuarioSerializer, LoginUsuarioSerializer
from .models import Usuario

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

class UsuarioDetailView(APIView):
    """
    Solo los superusuarios pueden acceder a los detalles de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get_object(self, pk):
        try:
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            usuario = self.get_object(pk)
            if not usuario:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            return Response(RegistroUsuarioSerializer(usuario).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UsuarioUpdateView(APIView):
    """
    Solo los superusuarios pueden acceder a los detalles de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get_object(self, nombre_usuario):
        try:
            return Usuario.objects.get(nombre_usuario=nombre_usuario)
        except Usuario.DoesNotExist:
            return None

    def update(self, request, nombre_usuario):
        try:
            usuario = self.get_object(nombre_usuario)
            if not usuario:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            serializer = RegistroUsuarioSerializer(usuario, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsuarioDeleteView(APIView):
    """
    Solo los superusuarios pueden acceder a los detalles de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get_object(self, nombre_usuario):
        try:
            return Usuario.objects.get(nombre_usuario=nombre_usuario)
        except Usuario.DoesNotExist:
            return None

    def delete(self, request, nombre_usuario):
        try:
            usuario = self.get_object(nombre_usuario)
            if not usuario:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            usuario.delete()
            return Response({"mensaje": "Usuario eliminado exitosamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

class UsuarioAllView(APIView):
    """
    Solo los superusuarios pueden ver todos los usuarios.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]
    
    def get(self, request):
        try:
            usuarios = Usuario.objects.all()
            serializer = RegistroUsuarioSerializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
