# ETL Fandit - Sistema de procesamiento de datos

Este componente se encarga de extraer datos de la API de Fandit (sobre subvenciones), transformarlos y cargarlos en la base de datos Aurora MySQL para su uso por el chatbot.

## Estructura del módulo

```
etl_fandit/
├── __init__.py             # Inicializador del paquete
├── api_to_json.py          # Utilidades para convertir respuestas API a JSON
├── clase_apifandit.py      # Cliente asíncrono para API Fandit
├── cronotab                # Configuración de tareas programadas
├── db_data_load.py         # Script para carga de datos en BD
├── db_setup.py             # Inicialización y configuración de la BD
├── docker-compose.yml      # Configuración Docker específica del ETL
├── Dockerfile              # Definición del contenedor ETL
├── eda_fandit.py           # Script de análisis exploratorio de datos
├── entrypoint.sh           # Script de inicio del contenedor
├── etl_fandit.py           # Script principal del proceso ETL
├── README_ETL.md           # Esta documentación
├── requirements.txt        # Dependencias de Python
├── setup_instructions.txt  # Instrucciones adicionales de configuración
├── output/                 # Directorio para archivos de salida
│   ├── api_assestment.txt  # Evaluación de la API
│   └── ...                 # Archivos de resultados (.json, .csv, .ods)
└── tests/                  # Pruebas del sistema ETL
    ├── test_api.py         # Pruebas de integración con la API
    └── ...                 # Pruebas adicionales
```

## Funcionalidad

El ETL de Fandit realiza las siguientes operaciones:

1. **Extracción**: Obtiene datos de subvenciones de la API de Fandit mediante peticiones HTTP.
2. **Transformación**: Procesa y formatea los datos para ajustarlos al esquema de la base de datos.
3. **Carga**: Almacena los datos en Aurora MySQL, detectando cambios para minimizar operaciones.
4. **Respaldo**: Guarda copias de los datos en formato JSON y CSV para auditoría y análisis.

## Configuración

### Archivo .env

El módulo ETL requiere un archivo `.env` con las siguientes variables:

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

La ejecución automatizada del ETL se controla mediante el archivo `cronotab` y la variable de entorno `ENABLE_AUTO_ETL` en el docker-compose principal.

### Ejecución manual

Para ejecutar el ETL manualmente:

```bash
# Desde la raíz del proyecto (usando Docker)
docker exec etl-fandit python /app/etl_fandit.py

# En entorno de desarrollo local
python etl_fandit.py
```

## Monitoreo y logs

Los logs del ETL se almacenan en dos ubicaciones:

1. **Logs del contenedor**: Accesibles mediante `docker logs etl-fandit`
2. **Logs de ejecución**: Guardados en `./output/etl_YYYYMMDD.log`

## Estructura de la base de datos

El ETL crea y mantiene una tabla `grants` en Aurora MySQL con los siguientes campos principales:

- `slug`: Identificador único de la subvención (clave primaria)
- `formatted_title`: Título de la subvención
- `status_text`: Estado actual (abierta, cerrada, etc.)
- `scope`: Ámbito geográfico (Estatal, Comunidad Autónoma)
- `request_amount`: Importe máximo solicitado
- Otros campos descriptivos y de condiciones

## Desarrollo y testing

### Pruebas

El directorio `tests/` contiene scripts para probar diferentes aspectos del ETL:

```bash
# Ejecutar pruebas de la API
python -m tests.test_api
```

### Análisis exploratorio

Para realizar un análisis de los datos extraídos:

```bash
python eda_fandit.py
```

## Solución de problemas

### Errores comunes

1. **Error de conexión a la API**
   - Verificar tokens en el archivo `.env`
   - Comprobar límites de la API y cuota disponible

2. **Error de conexión a la base de datos**
   - Verificar credenciales de Aurora en `.env`
   - Comprobar que el cluster esté activo y accesible

3. **ETL no ejecuta automáticamente**
   - Verificar que `ENABLE_AUTO_ETL=true` en docker-compose
   - Comprobar formato correcto en archivo `cronotab`