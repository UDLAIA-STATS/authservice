from decouple import config
from math import ceil
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from ldclient import Context
from authservice.launchdarkly import ld_client
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from .serializers import RegistroUsuarioSerializer, LoginUsuarioSerializer
from .models import Usuario
from .utils import error_response, success_response, pagination_response, format_serializer_errors

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
        try:
            serializer = RegistroUsuarioSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
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
        except ValidationError as ve:
            errors = format_serializer_errors(ve.message_dict)
            return error_response(
                data=None,
                message=errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError:
            return error_response(
                data=None,
                message='El usuario o correo ya están registrados.',
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return error_response(
                data=None,
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )


class UsuarioDetailView(APIView):
    """
    Solo los superusuarios pueden acceder a los detalles de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get_object(self, nombre_usuario):
        """
        Retorna el usuario correspondiente al nombre de usuario.
        """
        return get_object_or_404(Usuario, nombre_usuario=nombre_usuario)

    def get(self, request, nombre_usuario):
        """
        Obtiene los detalles de un usuario por su nombre de usuario.
        """
        try:
            usuario = self.get_object(nombre_usuario)
            serializer = RegistroUsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UsuarioUpdateView(APIView):
    """
    Solo los superusuarios pueden acceder a los detalles de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get_object(self, nombre_usuario):
        return get_object_or_404(Usuario, nombre_usuario=nombre_usuario)

    def patch(self, request, nombre_usuario):
        """
        Actualiza un usuario por su nombre de usuario.
        
        Solo los superusuarios pueden acceder a esta vista.
        
        Parámetros:
            nombre_usuario (str): nombre de usuario del usuario a actualizar.
        
        Retorna:
            Response: respuesta con los detalles del usuario actualizado.
        """
        try:
            usuario = self.get_object(nombre_usuario)
            serializer = RegistroUsuarioSerializer(usuario, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            errors = format_serializer_errors(ve.message_dict)
            return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsuarioDeleteView(APIView):
    """
    Solo los superusuarios pueden acceder a los detalles de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get_object(self, nombre_usuario):
        return get_object_or_404(Usuario, nombre_usuario=nombre_usuario)


    def delete(self, request, nombre_usuario):
        try:
            usuario = self.get_object(nombre_usuario)
            data = request.data
            data['is_active'] = False
            serializer = RegistroUsuarioSerializer(usuario, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"mensaje": "Usuario eliminado exitosamente"}, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            errors = format_serializer_errors(ve.message_dict)
            return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class UsuarioAllView(APIView):
    """
    Solo los superusuarios pueden ver todos los usuarios.
    Permite paginar resultados con los parámetros:
    - ?page=<número de página>
    - ?offset=<cantidad de items por página>
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get(self, request):
        """
        Lista todos los usuarios con paginación.

        Parámetros:
            ?page=<número de página>
            ?offset=<cantidad de items por página>

        Retorna:
            Response: respuesta con los detalles de los usuarios y la paginación.
        """
        try:
            page = int(request.query_params.get('page', 1))
            offset = int(request.query_params.get('offset', 10))

            if page < 1 or offset < 1:
                return Response(
                    {"error": "Los parámetros 'page' y 'offset' deben ser mayores a 0."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            usuarios = Usuario.objects.all().order_by('id')

            total_items = usuarios.count()
            total_pages = ceil(total_items / offset)

            start = (page - 1) * offset
            end = start + offset

            usuarios_paginados = usuarios[start:end]

            # Serializar los datos
            serializer = RegistroUsuarioSerializer(usuarios_paginados, many=True)

            response_data = {
                "items": serializer.data,
                "pagination": {
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "current_page": page,
                    "offset": offset,
                    "has_next": page < total_pages,
                    "has_previous": page > 1,
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {"error": "Los parámetros 'page' y 'offset' deben ser enteros."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginUsuarioView(APIView):
    """
    Permite que profesores y superusuarios inicien sesión.
    Devuelve el token y los datos del usuario.
    """
    def post(self, request):
        try: 
            serializer = LoginUsuarioSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)    
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'usuario': {
                    'id': user.id, #type: ignore
                    'nombre_usuario': user.nombre_usuario, #type: ignore
                    'email_usuario': user.email_usuario, #type: ignore
                    'rol': user.rol #type: ignore
                },
                'token': token.key
            }, status=status.HTTP_200_OK)
        except ValidationError as ve:
            errors = format_serializer_errors(ve.message_dict)
            return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestDarklyView(APIView):
    """
    Vista de prueba para LaunchDarkly.
    """
    permission_classes = [permissions.IsAuthenticated, EsSuperUsuario]

    def get(self, request):
        try:
            client = ld_client()
            if not client.is_initialized():
                print('SDK failed to initialize')
                return Response({"error": "Falló la inicialización del SDK de LaunchDarkly"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
            context = (
                Context.builder('user-key-123abcde')
                .kind('user')
                .set('email', 'biz@face.dev')
                .build()
            )

            # Tracking your memberId lets us know you are connected.
            ld_client().track('692cd78a64545909c597ca31', context)
            print('SDK successfully initialized')
            return Response({"mensaje": "LaunchDarkly SDK inicializado correctamente"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
