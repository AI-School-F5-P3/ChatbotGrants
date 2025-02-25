# Proyecto Integrado - Aplicación Web con ETL Fandit

Este proyecto contiene una aplicación web completa con frontend, backend y un sistema ETL para procesar datos de la API de Fandit y almacenarlos en Aurora DB.

## Estructura del Proyecto

```
proyecto-principal/
│
├── docker-compose.yml      # Archivo docker-compose integrado 
│
├── backend/                # Código del backend
│
├── frontend/               # Código del frontend
│
└── etl-fandit/             # ETL para la API Fandit
    ├── Dockerfile          # Definición del contenedor ETL
    ├── requirements.txt    # Dependencias de Python
    ├── crontab             # Programación de tareas
    ├── entrypoint.sh       # Script de inicio
    ├── etl_fandit.py       # Script principal ETL
    ├── clase_apifandit.py  # Clase para API Fandit
    ├── .env                # Variables de entorno (credenciales)
    ├── output/             # Directorio para los archivos JSON
    └── logs/               # Directorio para los logs
```

## Componentes

### 1. Frontend

Aplicación web que se ejecuta en el puerto 80.

### 2. Backend API

Servicio de API que se ejecuta en el puerto 8000 y proporciona datos a la aplicación frontend.

### 3. ETL Fandit

Servicio que extrae datos de la API de Fandit, los transforma y los carga en la base de datos Aurora.

## Configuración del ETL

### Archivo .env

El ETL requiere un archivo `.env` en el directorio `etl-fandit/` con las siguientes variables:

```
FANDIT_TOKEN=tu_token_aquí
FANDIT_EXPERT_TOKEN=tu_expert_token_aquí
FANDIT_EMAIL=tu_email@ejemplo.com
FANDIT_PASSWORD=tu_password
AURORA_CLUSTER_ENDPOINT=tu_endpoint_de_aurora
DB_USER=tu_usuario_db
DB_PASSWORD=tu_password_db
```

### Ejecución automática

Por defecto, la ejecución automática está **desactivada**. Para activarla:

1. Edita el archivo `docker-compose.yml`
2. Cambia `ENABLE_AUTO_ETL=false` a `ENABLE_AUTO_ETL=true`
3. Reinicia los servicios: `docker-compose up -d`

## Uso

### Iniciar todos los servicios

```bash
docker-compose up -d
```

### Ejecutar el ETL manualmente

```bash
docker exec etl-fandit python /app/etl_fandit.py
```

### Ver logs del ETL

```bash
# Ver logs del contenedor
docker logs etl-fandit

# Ver logs de la última ejecución del ETL
docker exec etl-fandit cat /app/logs/etl_$(date +%Y%m%d).log
```

### Detener todos los servicios

```bash
docker-compose down
```

## Programación del ETL

El ETL está configurado para ejecutarse automáticamente (cuando se activa):
- Todos los días a las 12:00 (Hora de Madrid)
- Los resultados se guardan en `./etl-fandit/logs/etl_YYYYMMDD.log`
- Los archivos JSON de respaldo se guardan en `./etl-fandit/output/`

## Personalización

Para cambiar la hora de ejecución del ETL:
1. Edita el archivo `etl-fandit/crontab`
2. Modifica la expresión cron `0 12 * * *` según tus necesidades
3. Reconstruye la imagen: `docker-compose build etl-fandit`
4. Reinicia los servicios: `docker-compose up -d`