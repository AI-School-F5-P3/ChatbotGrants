import json
import mysql.connector
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def connect_db():
    """Establece conexión con la base de datos grants_db"""
    return mysql.connector.connect(
        host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database='grants_db'
    )

def insert_grants(cursor, grants_data):
    """Inserta los datos en la tabla grants"""
    insert_query = """
    INSERT INTO grants (
        slug, formatted_title, status_text, entity, total_amount,
        request_amount, goal_extra, scope, publisher, applicants,
        term, help_type, expenses, fund_execution_period, line,
        extra_limit, info_extra
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    for grant in grants_data:
        values = (
            grant['slug'],
            grant['formatted_title'],
            grant['status_text'],
            grant['entity'],
            grant['total_amount'],
            grant['request_amount'],
            grant['goal_extra'],
            grant['scope'],
            grant['publisher'],
            grant['applicants'],
            grant['term'],
            grant['help_type'],
            grant['expenses'],
            grant['fund_execution_period'],
            grant['line'],
            grant['extra_limit'],
            grant['info_extra']
        )
        
        try:
            cursor.execute(insert_query, values)
            logger.info(f"Insertado registro con slug: {grant['slug']}")
        except mysql.connector.Error as err:
            logger.error(f"Error insertando registro {grant['slug']}: {err}")

def import_data():
    """Importa los datos del archivo JSON a la base de datos"""
    try:
        # Leer el archivo JSON
        with open('subvenciones_20250220_111707.json', 'r', encoding='utf-8') as file:
            grants_data = json.load(file)
            
        logger.info(f"Leyendo {len(grants_data)} registros del archivo JSON")
        
        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor()
        
        # Insertar los datos
        insert_grants(cursor, grants_data)
        
        # Commit de los cambios
        conn.commit()
        logger.info("Importación completada exitosamente")
        
    except mysql.connector.Error as err:
        logger.error(f"Error de base de datos: {err}")
        if 'conn' in locals():
            conn.rollback()
    except Exception as e:
        logger.error(f"Error general: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    import_data()