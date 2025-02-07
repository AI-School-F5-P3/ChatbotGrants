import mysql.connector
import os
from dotenv import load_dotenv
import logging
import socket

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

def test_connection():
    try:
        # Probar resolución de DNS
        ip_address = socket.gethostbyname(os.getenv('AURORA_CLUSTER_ENDPOINT'))
        logger.info(f"IP resuelta: {ip_address}")

        # Parámetros de conexión
        conn_params = {
            'host': os.getenv('AURORA_CLUSTER_ENDPOINT'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': 3306,
            'connect_timeout': 10
        }

        # Conexión
        logger.info("Intentando conectar...")
        conn = mysql.connector.connect(**conn_params)
        logger.info("Conexión exitosa")
        
        # Verificar versión del servidor
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        logger.info(f"Versión del servidor MySQL: {version[0]}")

        cursor.close()
        conn.close()

    except socket.gaierror as e:
        logger.error(f"Error de resolución de DNS: {e}")
    except mysql.connector.Error as err:
        logger.error(f"Error de conexión MySQL: {err}")
        if err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
            logger.error("No se pudo conectar al host. Verificar endpoint y configuración de red.")
        elif err.errno == mysql.connector.errorcode.CR_CONN_TIMEOUT:
            logger.error("La conexión ha excedido el tiempo de espera. Verificar firewall y configuraciones de red.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

def setup_database():
    try:
        # Conectar sin especificar base de datos
        conn = mysql.connector.connect(
            host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=3306,
            connect_timeout=10
        )
        cursor = conn.cursor()

        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS fandit_db")
        logger.info("Base de datos creada o verificada")
        
        # Cambiar a la base de datos
        cursor.execute("USE fandit_db")
        
        # Crear tabla
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS funds (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fund_id VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            description TEXT,
            total_amount DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        logger.info("Tabla funds creada exitosamente")
        
        conn.commit()
        logger.info("Configuración de base de datos completada")

    except mysql.connector.Error as err:
        logger.error(f"Error en la configuración de la base de datos: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Primero probar la conexión
    test_connection()
    # Luego configurar la base de datos
    setup_database()