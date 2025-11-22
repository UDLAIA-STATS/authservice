#!/usr/bin/env bash
set -e

# Cargar .env si existe dentro de /app (opcional)
if [ -f /app/.env ]; then
  set -a
  . /app/.env
  set +a
fi

echo "Esperando a Postgres en $POSTGRES_HOST:$POSTGRES_PORT..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done
echo "Postgres disponible."

# Aplicar migraciones
python manage.py migrate --noinput

# Crear superusuario solo si no existe
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
python <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(nombre_usuario="administrador").exists():
    User.objects.create_superuser(
        "administrador",
        "admin@gmail.com",
        "$DJANGO_SUPERUSER_PASSWORD"
    )
EOF
fi

# Iniciar Django (puedes cambiar a gunicorn si es para prod)
exec python manage.py runserver 0.0.0.0:8010
