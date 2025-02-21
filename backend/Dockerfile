FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY etl_fandit.py .
COPY clase_apifandit.py .
COPY .env .

# Crear directorio para logs y output
RUN mkdir -p /app/output /app/logs

# Configurar cron
COPY crontab /etc/cron.d/etl-cron
RUN chmod 0644 /etc/cron.d/etl-cron \
    && crontab /etc/cron.d/etl-cron

# Comando para iniciar tanto el script como cron
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Ejecutar el script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]