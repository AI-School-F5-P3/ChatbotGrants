import asyncio
import json
import os
import logging
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
from clase_apifandit import FanditAPI

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_fandit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ETL_Fandit")

# Cargar variables de entorno
load_dotenv()

def connect_db():
    """Establece conexión con la base de datos grants_db"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database='grants_db'
        )
        logger.info("Conexión a la base de datos establecida correctamente")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error al conectar a la base de datos: {err}")
        raise

def get_existing_grants(cursor):
    """
    Obtiene todos los grants existentes en la base de datos
    Retorna un diccionario {slug: {datos completos}}
    """
    # Obtener todos los grants
    query = "SELECT * FROM grants"
    cursor.execute(query)
    
    # Obtener nombres de columnas
    column_names = [column[0] for column in cursor.description]
    
    # Crear diccionario de grants existentes
    existing_grants = {}
    for row in cursor.fetchall():
        # Convertir la fila a un diccionario
        grant_dict = dict(zip(column_names, row))
        existing_grants[grant_dict['slug']] = grant_dict
    
    logger.info(f"Se encontraron {len(existing_grants)} grants existentes en la base de datos")
    return existing_grants

async def descargar_subvenciones(api, paginas_a_descargar=None):
    """
    Descarga subvenciones de la API de Fandit.
    
    :param api: Instancia de FanditAPI
    :param paginas_a_descargar: Número de páginas a descargar (None para todas)
    :return: Lista completa de subvenciones
    """
    todas_subvenciones = []
    
    filtros_base = {
        "is_open": True,
        "start_date": None,
        "end_date": None,
        "final_period_start_date": None,
        "final_period_end_date": None,
        "provinces": [],
        "applicants": [],
        "communities": [],
        "action_items": [],
        "origins": [],
        "activities": [],
        "region_types": [],
        "types": []
    }
    
    # Obtener primera página para ver el total
    primera_respuesta = await api.obtener_lista_subvenciones(page=1, request_data=filtros_base)
    if not primera_respuesta:
        logger.error("No se pudo obtener la primera página")
        return []
        
    total_registros = primera_respuesta.get('count', 0)
    registros_por_pagina = len(primera_respuesta.get('results', []))
    total_paginas = -(-total_registros // registros_por_pagina)  # Redondeo hacia arriba
    
    logger.info(f"Total de registros disponibles: {total_registros}")
    logger.info(f"Registros por página: {registros_por_pagina}")
    logger.info(f"Total de páginas: {total_paginas}")
    
    # Añadir resultados de la primera página
    todas_subvenciones.extend(primera_respuesta.get('results', []))
    
    # Descargar el resto de páginas
    max_paginas = paginas_a_descargar if paginas_a_descargar else total_paginas
    for pagina in range(2, max_paginas + 1):
        logger.info(f"Descargando página {pagina} de {max_paginas}...")
        
        respuesta = await api.obtener_lista_subvenciones(page=pagina, request_data=filtros_base)
        if respuesta and 'results' in respuesta:
            subvenciones_pagina = respuesta['results']
            todas_subvenciones.extend(subvenciones_pagina)
            
            if not respuesta.get('next'):
                logger.info("No hay más páginas disponibles")
                break
        else:
            logger.warning(f"No se encontraron resultados en la página {pagina}")
            break
            
        # Pequeña pausa para no sobrecargar la API
        await asyncio.sleep(0.5)
    
    logger.info(f"Total de subvenciones descargadas: {len(todas_subvenciones)}")
    return todas_subvenciones

def guardar_json_backup(datos, nombre_archivo=None):
    """
    Guarda los datos en un archivo JSON como respaldo.
    
    :param datos: Datos a guardar
    :param nombre_archivo: Nombre del archivo (si no se especifica, se usa la fecha actual)
    """
    if not nombre_archivo:
        # Crear nombre de archivo con fecha y hora actual
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"subvenciones_{fecha_actual}.json"
    
    # Crear directorio de salida si no existe
    os.makedirs('output', exist_ok=True)
    ruta_completa = os.path.join('output', nombre_archivo)
    
    with open(ruta_completa, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    
    logger.info(f"Datos guardados como respaldo en {ruta_completa}")

def identificar_cambios(subvenciones_api, existing_grants):
    """
    Identifica registros nuevos y actualizados comparando con los existentes en la BD.
    
    :param subvenciones_api: Lista de subvenciones obtenidas de la API
    :param existing_grants: Diccionario de subvenciones existentes en la BD
    :return: Tupla (nuevos, actualizados)
    """
    nuevos = []
    actualizados = []
    sin_cambios = 0
    
    # Campos a comparar para detectar cambios
    campos_comparacion = [
        'formatted_title', 'status_text', 'entity', 'total_amount',
        'request_amount', 'goal_extra', 'scope', 'publisher', 'applicants',
        'term', 'help_type', 'expenses', 'fund_execution_period', 'line',
        'extra_limit', 'info_extra'
    ]
    
    for subvencion in subvenciones_api:
        slug = subvencion['slug']
        
        # Verificar si es un registro nuevo
        if slug not in existing_grants:
            nuevos.append(subvencion)
            continue
        
        # Verificar si hay cambios en los campos relevantes
        cambio_detectado = False
        existing_grant = existing_grants[slug]
        
        for campo in campos_comparacion:
            if campo in subvencion and str(subvencion.get(campo, '')) != str(existing_grant.get(campo, '')):
                cambio_detectado = True
                break
        
        if cambio_detectado:
            actualizados.append(subvencion)
        else:
            sin_cambios += 1
    
    logger.info(f"Se identificaron {len(nuevos)} registros nuevos y {len(actualizados)} actualizados")
    logger.info(f"Registros sin cambios: {sin_cambios}")
    return nuevos, actualizados

def insertar_nuevos_grants(cursor, grants_nuevos):
    """
    Inserta los nuevos grants en la base de datos
    
    :param cursor: Cursor de la conexión a la BD
    :param grants_nuevos: Lista de grants nuevos a insertar
    """
    if not grants_nuevos:
        logger.info("No hay registros nuevos para insertar")
        return 0
    
    insert_query = """
    INSERT INTO grants (
        slug, formatted_title, status_text, entity, total_amount,
        request_amount, goal_extra, scope, publisher, applicants,
        term, help_type, expenses, fund_execution_period, line,
        extra_limit, info_extra, created_at, updated_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
    )
    """
    
    insertados = 0
    for grant in grants_nuevos:
        values = (
            grant.get('slug', ''),
            grant.get('formatted_title', ''),
            grant.get('status_text', ''),
            grant.get('entity', ''),
            grant.get('total_amount', 0),
            grant.get('request_amount', 0),
            grant.get('goal_extra', ''),
            grant.get('scope', ''),
            grant.get('publisher', ''),
            grant.get('applicants', ''),
            grant.get('term', ''),
            grant.get('help_type', ''),
            grant.get('expenses', ''),
            grant.get('fund_execution_period', ''),
            grant.get('line', ''),
            grant.get('extra_limit', ''),
            grant.get('info_extra', '')
        )
        
        try:
            cursor.execute(insert_query, values)
            insertados += 1
            logger.info(f"Insertado nuevo registro con slug: {grant['slug']}")
        except mysql.connector.Error as err:
            logger.error(f"Error insertando registro {grant['slug']}: {err}")
    
    return insertados

def actualizar_grants_modificados(cursor, grants_actualizados):
    """
    Actualiza los grants modificados en la base de datos
    
    :param cursor: Cursor de la conexión a la BD
    :param grants_actualizados: Lista de grants actualizados
    """
    if not grants_actualizados:
        logger.info("No hay registros para actualizar")
        return 0
    
    update_query = """
    UPDATE grants SET
        formatted_title = %s,
        status_text = %s,
        entity = %s,
        total_amount = %s,
        request_amount = %s,
        goal_extra = %s,
        scope = %s,
        publisher = %s,
        applicants = %s,
        term = %s,
        help_type = %s,
        expenses = %s,
        fund_execution_period = %s,
        line = %s,
        extra_limit = %s,
        info_extra = %s
    WHERE slug = %s
    """
    
    actualizados = 0
    for grant in grants_actualizados:
        values = (
            grant.get('formatted_title', ''),
            grant.get('status_text', ''),
            grant.get('entity', ''),
            grant.get('total_amount', 0),
            grant.get('request_amount', 0),
            grant.get('goal_extra', ''),
            grant.get('scope', ''),
            grant.get('publisher', ''),
            grant.get('applicants', ''),
            grant.get('term', ''),
            grant.get('help_type', ''),
            grant.get('expenses', ''),
            grant.get('fund_execution_period', ''),
            grant.get('line', ''),
            grant.get('extra_limit', ''),
            grant.get('info_extra', ''),
            grant.get('slug', '')  # WHERE condition
        )
        
        try:
            cursor.execute(update_query, values)
            actualizados += 1
            logger.info(f"Actualizado registro con slug: {grant['slug']}")
        except mysql.connector.Error as err:
            logger.error(f"Error actualizando registro {grant['slug']}: {err}")
    
    return actualizados

# Función eliminada - Ya no registramos en tabla aparte

async def main():
    start_time = datetime.now()
    logger.info(f"Iniciando proceso ETL Fandit a las {start_time}")
    
    # Obtener tokens y credenciales del archivo .env
    token = os.getenv('FANDIT_TOKEN')
    expert_token = os.getenv('FANDIT_EXPERT_TOKEN')
    email = os.getenv('FANDIT_EMAIL')
    password = os.getenv('FANDIT_PASSWORD')
    
    # Verificar que los tokens estén presentes
    if not token or not expert_token:
        logger.error("Error: Tokens no encontrados en el archivo .env")
        return
    
    # Inicializar la API con los tokens
    api = FanditAPI(
        token=token, 
        expert_token=expert_token, 
        email=email,  
        password=password  
    )
    
    try:
        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener grants existentes
        existing_grants = get_existing_grants(cursor)
        
        # Intentar renovar el token primero
        if email and password:
            await api.refrescar_token()
        
        # 1. Descargar lista de subvenciones (todas las páginas)
        subvenciones = await descargar_subvenciones(api, paginas_a_descargar=None)
        logger.info(f"Total de subvenciones base descargadas: {len(subvenciones)}")
        
        # Verificar si se descargaron subvenciones
        if not subvenciones:
            logger.error("No se descargaron subvenciones. Verificar credenciales y configuración.")
            return
        
        # 2. Guardar una copia de los datos como respaldo
        guardar_json_backup(subvenciones)
        
        # 3. Identificar registros nuevos y actualizados
        nuevos, actualizados = identificar_cambios(subvenciones, existing_grants)
        
        # Si no hay cambios, finalizar
        if not nuevos and not actualizados:
            logger.info("No se detectaron cambios en los datos, no es necesario actualizar la base de datos")
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"Proceso ETL completado sin cambios. Duración: {duration}")
            return
            
        # 4. Insertar nuevos registros
        nuevos_insertados = insertar_nuevos_grants(cursor, nuevos)
        
        # 5. Actualizar registros modificados
        registros_actualizados = actualizar_grants_modificados(cursor, actualizados)
        
        # Commit de los cambios
        conn.commit()
        logger.info("Cambios confirmados en la base de datos")
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Proceso ETL completado. Duración: {duration}")
        logger.info(f"Total registros procesados: {len(subvenciones)}")
        logger.info(f"Registros nuevos insertados: {nuevos_insertados}")
        logger.info(f"Registros actualizados: {registros_actualizados}")
        
    except Exception as e:
        logger.error(f"Error en el proceso ETL: {e}")
        # Imprimir información adicional de depuración
        import traceback
        logger.error(traceback.format_exc())
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            logger.info("Se ha realizado rollback de las transacciones")
    finally:
        # Cerrar cursor y conexión
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            logger.info("Conexión a la base de datos cerrada")

if __name__ == "__main__":
    asyncio.run(main())