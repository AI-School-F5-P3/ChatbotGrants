import mysql.connector
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def create_fund_details_table():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database='fandit_db'
        )
        cursor = conn.cursor()

        # Crear tabla fund_details
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fund_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            purpose TEXT,
            submission_period_opening DATE,
            submission_period_closing DATE,
            funds VARCHAR(100),
            scope VARCHAR(100),
            max_aid VARCHAR(50),
            official_info JSON,
            eligible_recipients JSON,
            covered_expenses JSON,
            additional_info JSON
        )
        """

        cursor.execute(create_table_sql)
        conn.commit()
        logger.info("Tabla fund_details creada exitosamente")

    except mysql.connector.Error as err:
        logger.error(f"Error al crear la tabla: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_fund_details_table()