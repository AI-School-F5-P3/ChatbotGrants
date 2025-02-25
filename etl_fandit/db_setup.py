import mysql.connector
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def connect_db():
    """Establece conexión con la base de datos"""
    return mysql.connector.connect(
        host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def create_database(cursor):
    """Crea la base de datos grants_db"""
    cursor.execute("CREATE DATABASE IF NOT EXISTS grants_db")
    cursor.execute("USE grants_db")
    logger.info("Base de datos grants_db creada/seleccionada exitosamente")

def create_grants_table(cursor):
    """Crea la tabla grants con la nueva estructura"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS grants (
        slug VARCHAR(255) PRIMARY KEY,
        formatted_title VARCHAR(255),
        status_text VARCHAR(255),
        entity VARCHAR(100),
        total_amount FLOAT,
        request_amount FLOAT,
        goal_extra TEXT,
        scope VARCHAR(50),
        publisher VARCHAR(255),
        applicants TEXT,
        term TEXT,
        help_type TEXT,
        expenses TEXT,
        fund_execution_period TEXT,
        line TEXT,
        extra_limit TEXT,
        info_extra TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    logger.info("Tabla grants creada exitosamente")

def setup_database():
    """Configura la base de datos y la tabla grants"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Crear la base de datos y seleccionarla
        create_database(cursor)
        
        # Crear la tabla grants
        create_grants_table(cursor)

        # Crear índices para mejorar el rendimiento
        cursor.execute("CREATE INDEX idx_formatted_title ON grants(formatted_title)")
        cursor.execute("CREATE INDEX idx_entity ON grants(entity)")
        cursor.execute("CREATE INDEX idx_status_text ON grants(status_text)")

        conn.commit()
        logger.info("Configuración de la base de datos completada exitosamente")

    except mysql.connector.Error as err:
        logger.error(f"Error en la configuración de la base de datos: {err}")
        raise
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()