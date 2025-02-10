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

        # Modificar tabla funds para ajustarla a la estructura de grants_search
        alter_table_sql = """
        ALTER TABLE funds 
        MODIFY COLUMN id INT AUTO_INCREMENT PRIMARY KEY,
        ADD COLUMN is_open BOOLEAN,
        ADD COLUMN description TEXT,
        ADD COLUMN max_budget DECIMAL(15,2),
        ADD COLUMN total_amount DECIMAL(15,2),
        ADD COLUMN min_total_amount DECIMAL(15,2),
        ADD COLUMN bdns VARCHAR(50),
        ADD COLUMN office VARCHAR(255),
        ADD COLUMN publication_date DATE,
        ADD COLUMN end_date DATE,
        ADD COLUMN search_tab INT,
        ADD COLUMN applicants JSON,
        ADD COLUMN action_items JSON,
        ADD COLUMN origins JSON,
        ADD COLUMN activities JSON,
        ADD COLUMN region_types JSON,
        ADD COLUMN types JSON
        """

        cursor.execute(alter_table_sql)
        conn.commit()
        logger.info("Tabla funds modificada exitosamente")

    except mysql.connector.Error as err:
        logger.error(f"Error al modificar la tabla: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    modify_funds_table()