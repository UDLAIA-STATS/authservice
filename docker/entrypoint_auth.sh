#!/usr/bin/env bash
set -e

# Si existe .env, exporta sus variables (POSIX)
if [ -f /app/.env ]; then
  set -a
  . /app/.env
  set +a
fi

# Espera corta opcional para asegurar DB (puedes ampliar si necesario)
# sleep 2

# Crear migraciones y aplicar migraciones (no interactivo)
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
export DJANGO_SUPERUSER_PASSWORD="administrador123"
python manage.py createsuperuser --noinput --username "administrador" --email "admin@gmail.com" || true

# Arrancar servidor (en dev uso runserver; reemplaza por gunicorn para producción)
exec python manage.py runserver 0.0.0.0:8010
