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
python manage.py makemigrations --noinput
# Crear superusuario solo si no existe
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_EMAIL" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
  echo "Creando superusuario usando parámetros CLI de Django..."
  python manage.py createsuperuser \
      --noinput \
      --username="$DJANGO_SUPERUSER_USERNAME" \
      --email="$DJANGO_SUPERUSER_EMAIL" \
      --password="$DJANGO_SUPERUSER_PASSWORD" || true
else
  echo "No se creará superusuario: faltan valores DJANGO_SUPERUSER_*"
fi

# Iniciar Django (puedes cambiar a gunicorn si es para prod)
exec python manage.py runserver 0.0.0.0:8010
