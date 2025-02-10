import mysql.connector
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def modify_funds_table():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database='fandit_db'
        )
        cursor = conn.cursor()

        # Lista de columnas adicionales a añadir
        columns_to_add = [
            "is_open BOOLEAN",
            "max_budget DECIMAL(15,2)",
            "bdns VARCHAR(50)",
            "office VARCHAR(255)",
            "publication_date DATE",
            "end_date DATE",
            "search_tab INT",
            "applicants JSON",
            "action_items JSON",
            "origins JSON",
            "activities JSON",
            "region_types JSON",
            "types JSON"
        ]

        # Intentar añadir columnas, ignorando errores si ya existen
        for column in columns_to_add:
            column_name = column.split()[0]
            try:
                alter_column_sql = f"ALTER TABLE funds ADD COLUMN {column}"
                cursor.execute(alter_column_sql)
                logger.info(f"Columna añadida: {column}")
            except mysql.connector.Error as err:
                if err.errno == 1060:  # Column already exists
                    logger.info(f"Columna ya existe: {column}")
                else:
                    logger.error(f"Error al añadir columna {column}: {err}")

        conn.commit()
        logger.info("Modificación de tabla funds completada")

    except mysql.connector.Error as err:
        logger.error(f"Error al modificar la tabla: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    modify_funds_table()