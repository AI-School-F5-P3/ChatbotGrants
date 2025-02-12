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
        password=os.getenv('DB_PASSWORD'),
        database='fandit_db'
    )

def create_funds_table(cursor):
    """Crea la tabla funds basada en la estructura del endpoint /funds/"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS funds (
        id INT AUTO_INCREMENT PRIMARY KEY,
        slug VARCHAR(255) UNIQUE,
        title VARCHAR(255),
        is_open BOOLEAN,
        max_budget DECIMAL(15,2),
        bdns VARCHAR(50),
        office VARCHAR(255),
        publication_date DATE,
        end_date DATE,
        final_period_start_date DATE,
        final_period_end_date DATE,
        search_tab INT,
        provinces JSON,
        communities JSON,
        applicants JSON,
        action_items JSON,
        origins JSON,
        activities JSON,
        region_types JSON,
        types JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    logger.info("Tabla funds creada/actualizada exitosamente")

def create_fund_details_table(cursor):
    """Crea la tabla fund_details basada en la estructura del endpoint /fund-details/<fund_slug>/"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS fund_details (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fund_slug VARCHAR(255),
        title VARCHAR(255),
        purpose TEXT,
        submission_period_opening DATE,
        submission_period_closing DATE,
        funds VARCHAR(100),
        scope TEXT,
        max_aid VARCHAR(100),
        official_info JSON,
        eligible_recipients JSON,
        covered_expenses JSON,
        additional_info JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (fund_slug) REFERENCES funds(slug) ON DELETE CASCADE
    )
    """
    cursor.execute(create_table_sql)
    logger.info("Tabla fund_details creada/actualizada exitosamente")

def create_concessions_table(cursor):
    """Crea la tabla concessions basada en la estructura del endpoint /funds/concessions/"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS concessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fund_slug VARCHAR(255),
        convocatoria VARCHAR(255),
        title VARCHAR(255),
        beneficiary VARCHAR(255),
        nif VARCHAR(50),
        amount DECIMAL(15,2),
        region VARCHAR(100),
        province VARCHAR(100),
        municipality VARCHAR(100),
        grant_date DATE,
        project_title TEXT,
        investment DECIMAL(15,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (fund_slug) REFERENCES funds(slug) ON DELETE CASCADE
    )
    """
    cursor.execute(create_table_sql)
    logger.info("Tabla concessions creada/actualizada exitosamente")

def create_beneficiaries_table(cursor):
    """Crea la tabla beneficiaries basada en la estructura del endpoint /funds/concessions/beneficiaries/"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS beneficiaries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nif VARCHAR(50) UNIQUE,
        name VARCHAR(255),
        total_grants INT,
        total_amount DECIMAL(15,2),
        regions JSON,
        projects JSON,
        fund_types JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    logger.info("Tabla beneficiaries creada/actualizada exitosamente")

def setup_database():
    """Configura todas las tablas de la base de datos"""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Crear las tablas en orden para mantener las relaciones
        create_funds_table(cursor)
        create_fund_details_table(cursor)
        create_concessions_table(cursor)
        create_beneficiaries_table(cursor)

        # Crear índices adicionales para mejorar el rendimiento
        cursor.execute("CREATE INDEX idx_fund_slug ON funds(slug)")
        cursor.execute("CREATE INDEX idx_fund_title ON funds(title)")
        cursor.execute("CREATE INDEX idx_concessions_nif ON concessions(nif)")
        cursor.execute("CREATE INDEX idx_beneficiaries_name ON beneficiaries(name)")

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