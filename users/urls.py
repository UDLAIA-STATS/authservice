from django.urls import path
from .views import RegistroUsuarioView, LoginUsuarioView, TestDarklyView, UsuarioAllView, UsuarioDeleteView, UsuarioDetailView, UsuarioUpdateView

urlpatterns = [
    path('register/', RegistroUsuarioView.as_view(), name='registro-usuario'),
    path('login/', LoginUsuarioView.as_view(), name='login-usuario'),
    path('users/', UsuarioAllView.as_view(), name='usuarios'),
    path('users/<str:nombre_usuario>/', UsuarioDetailView.as_view(), name='usuario-detalle'),
    path('users/<str:nombre_usuario>/update/', UsuarioUpdateView.as_view(), name='usuario-actualizar'),
    path('users/<str:nombre_usuario>/delete/', UsuarioDeleteView.as_view(), name='usuario-eliminar'),
    path('ld-test/', TestDarklyView.as_view(), name='launchdarkly-test'),
]
