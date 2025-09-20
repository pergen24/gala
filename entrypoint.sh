#!/bin/bash
set -e

HOST=${DB_HOST:-db}
PORT=${DB_PORT:-5432}

echo "Esperando a que PostgreSQL esté listo en $HOST:$PORT..."

while ! nc -z $HOST $PORT; do
  echo "Postgres no está listo todavía. Esperando 2s..."
  sleep 2
done

echo "PostgreSQL está listo. Aplicando migraciones..."

# Aplica migraciones
flask db upgrade

echo "Iniciando la app Flask..."
exec flask run --host=0.0.0.0 --port=5000
