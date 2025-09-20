FROM python:3.11-slim

WORKDIR /app

# Dependencias necesarias para compilar pycairo y reportlab + netcat
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libcairo2-dev \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda la app
COPY . .

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Variables de entorno de Flask
ENV FLASK_APP=manage.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Exponer puerto
EXPOSE 5000

# Usar entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
