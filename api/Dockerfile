
FROM python:3.11-slim

WORKDIR /app

# Instalar cliente SSH
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY app.py .
COPY cargar_resultados.py .

# Puerto de Flask
EXPOSE 5000

# Iniciar API
CMD ["python", "app.py"]
