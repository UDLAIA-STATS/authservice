FROM python:3.13-slim

# Evitar prompts debian
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copiamos requirements primero para aprovechar cache
COPY requirements.txt /app/requirements.txt

# Instalar dependencias del sistema necesarias y pip deps (libpq para psycopg)
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev gcc bash \
 && pip install --no-cache-dir -r /app/requirements.txt \
 && apt-get purge -y --auto-remove gcc \
 && rm -rf /var/lib/apt/lists/*

# Copiamos el código
COPY . /app

# Copiamos el .env (si lo mantienes fuera, el docker-compose puede montar)
COPY .env /app/.env

# entrypoint para cargar .env y ejecutar makemigrations/migrate/start
COPY docker/entrypoint_auth.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8010

# Usamos un entrypoint script para que se haga la secuencia necesaria
CMD ["/app/entrypoint.sh"]
