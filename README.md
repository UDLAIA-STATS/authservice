# AuthService - Microservicio de Autenticación

## Descripción

AuthService es un microservicio de autenticación y gestión de usuarios desarrollado con Django REST Framework. Este microservicio forma parte de una arquitectura de microservicios y se encarga de:

- Gestión de usuarios (profesores y superusuarios)
- Autenticación mediante tokens
- Control de acceso basado en roles
- Operaciones CRUD sobre usuarios

## Características

- **Autenticación basada en tokens**: Utiliza Django REST Framework Token Authentication
- **Control de acceso por roles**: Dos tipos de usuarios (profesor y superusuario)
- **API RESTful**: Endpoints bien definidos para todas las operaciones
- **Paginación**: Soporte de paginación en listado de usuarios
- **Soft delete**: Los usuarios se desactivan en lugar de eliminarse permanentemente

## Roles de Usuario

- **Superusuario**: Acceso completo a todas las operaciones (crear, leer, actualizar, eliminar usuarios)
- **Profesor**: Usuario estándar con acceso limitado

## Requisitos de Autenticación

**IMPORTANTE**: Todos los endpoints excepto `/api/login/` requieren autenticación mediante token.

Para autenticarte, debes incluir el header `Authorization` en tus peticiones:
```
Authorization: Token <tu_token_aqui>
```

El token se obtiene al iniciar sesión exitosamente.

## Endpoints Disponibles

### 1. Login
**POST** `/api/login/`

Permite que profesores y superusuarios inicien sesión.

**No requiere autenticación**

**Body:**
```json
{
  "nombre_usuario": "admin",
  "contrasenia_usuario": "password123"
}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Inicio de sesión exitoso",
  "usuario": {
    "id": 1,
    "nombre_usuario": "admin",
    "email_usuario": "admin@example.com",
    "rol": "superuser"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### 2. Registrar Usuario
**POST** `/api/register/`

Crea un nuevo usuario. **Solo superusuarios pueden acceder**.

**Requiere autenticación con rol de superusuario**

**Body:**
```json
{
  "nombre_usuario": "profesor1",
  "email_usuario": "profesor1@example.com",
  "contrasenia_usuario": "password123",
  "rol": "profesor"
}
```

**Respuesta exitosa (201):**
```json
{
  "mensaje": "Usuario creado exitosamente",
  "usuario": {
    "id": 2,
    "nombre_usuario": "profesor1",
    "email_usuario": "profesor1@example.com",
    "rol": "profesor"
  },
  "token": "a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4"
}
```

### 3. Listar Todos los Usuarios
**GET** `/api/users/`

Obtiene la lista de usuarios con paginación. **Solo superusuarios pueden acceder**.

**Requiere autenticación con rol de superusuario**

**Parámetros de query:**
- `page` (opcional, default: 1): Número de página
- `offset` (opcional, default: 10): Cantidad de items por página

**Respuesta exitosa (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre_usuario": "admin",
      "email_usuario": "admin@example.com",
      "rol": "superuser",
      "is_active": true
    },
    {
      "id": 2,
      "nombre_usuario": "profesor1",
      "email_usuario": "profesor1@example.com",
      "rol": "profesor",
      "is_active": true
    }
  ],
  "pagination": {
    "total_items": 15,
    "total_pages": 2,
    "current_page": 1,
    "offset": 10,
    "has_next": true,
    "has_previous": false
  }
}
```

### 4. Obtener Detalle de Usuario
**GET** `/api/users/<nombre_usuario>/`

Obtiene los detalles de un usuario específico. **Solo superusuarios pueden acceder**.

**Requiere autenticación con rol de superusuario**

**Respuesta exitosa (200):**
```json
{
  "id": 2,
  "nombre_usuario": "profesor1",
  "email_usuario": "profesor1@example.com",
  "rol": "profesor",
  "is_active": true
}
```

### 5. Actualizar Usuario
**PATCH** `/api/users/<nombre_usuario>/update/`

Actualiza los datos de un usuario. **Solo superusuarios pueden acceder**.

**Requiere autenticación con rol de superusuario**

**Body (todos los campos son opcionales):**
```json
{
  "email_usuario": "nuevo_email@example.com",
  "contrasenia_usuario": "nueva_password",
  "rol": "profesor"
}
```

**Respuesta exitosa (200):**
```json
{
  "id": 2,
  "nombre_usuario": "profesor1",
  "email_usuario": "nuevo_email@example.com",
  "rol": "profesor",
  "is_active": true
}
```

### 6. Eliminar Usuario (Soft Delete)
**DELETE** `/api/users/<nombre_usuario>/delete/`

Desactiva un usuario (no lo elimina físicamente). **Solo superusuarios pueden acceder**.

**Requiere autenticación con rol de superusuario**

**Respuesta exitosa (204):**
```json
{
  "mensaje": "Usuario eliminado exitosamente"
}
```

## Ejemplos de uso con cURL

### Login
```bash
curl -X POST http://localhost:8010/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_usuario": "admin",
    "contrasenia_usuario": "password123"
  }'
```

### Registrar Usuario (requiere token de superusuario)
```bash
curl -X POST http://localhost:8010/api/register/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -d '{
    "nombre_usuario": "profesor1",
    "email_usuario": "profesor1@example.com",
    "contrasenia_usuario": "password123",
    "rol": "profesor"
  }'
```

### Listar Usuarios con Paginación
```bash
curl -X GET "http://localhost:8010/api/users/?page=1&offset=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Obtener Detalle de Usuario
```bash
curl -X GET http://localhost:8010/api/users/profesor1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Actualizar Usuario
```bash
curl -X PATCH http://localhost:8010/api/users/profesor1/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -d '{
    "email_usuario": "nuevo_email@example.com"
  }'
```

### Eliminar Usuario
```bash
curl -X DELETE http://localhost:8010/api/users/profesor1/delete/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

## Imagen de Docker

La imagen de Docker está disponible en Docker Hub:

**https://hub.docker.com/repository/docker/dase123/udlaia-stats/tags/**

**Nombre de la imagen:** `dase123/udlaia-stats:authservice`

## Ejecutar Localmente con Docker

### Usando Docker Run
```bash
docker run -d --name authservice -p 8010:8010 \
  -e DB_ENGINE=django.db.backends.postgresql \
  -e POSTGRES_HOST=localhost \
  -e POSTGRES_PORT=5440 \
  -e POSTGRES_DB=udlafutbolappusuarios \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=0000 \
  dase123/udlaia-stats:authservice
```

### Variables de Entorno Requeridas

- `DB_ENGINE`: Motor de base de datos (default: `django.db.backends.postgresql`)
- `POSTGRES_HOST`: Host de PostgreSQL
- `POSTGRES_PORT`: Puerto de PostgreSQL
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_USER`: Usuario de PostgreSQL
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `DJANGO_SUPERUSER_PASSWORD`: Contraseña por defecto para crear superusuarios cuando no se proporciona una contraseña

## Tecnologías Utilizadas

- **Django 5.0**: Framework web
- **Django REST Framework**: Framework para APIs REST
- **PostgreSQL**: Base de datos
- **Token Authentication**: Sistema de autenticación
- **Docker**: Contenedorización

## Puerto

El microservicio corre en el puerto **8010** por defecto.
