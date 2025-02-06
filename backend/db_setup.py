import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
import mysql.connector

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = os.getenv('DB_HOST')
    database: str = os.getenv('DB_NAME')
    user: str = os.getenv('DB_USER')
    password: str = os.getenv('DB_PASSWORD')
    port: str = os.getenv('DB_PORT')

class DatabaseSetup:
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def setup_database(self):
        """Configurar la base de datos y las tablas"""
        self._create_database_if_not_exists()
        self._create_table()
        self._create_indexes()

    def _create_database_if_not_exists(self):
        """Crear la base de datos si no existe"""
        try:
            conn = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.database}")
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Base de datos {self.config.database} creada/verificada")
        except Exception as e:
            logger.error(f"Error creando la base de datos: {str(e)}")
            raise

    def _create_table(self):
        """Crear la tabla funds"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS funds (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fund_id VARCHAR(255) UNIQUE,
            is_open BOOLEAN,
            search_by_text TEXT,
            max_budget DECIMAL(15,2),
            max_total_amount DECIMAL(15,2),
            min_total_amount DECIMAL(15,2),
            bdns TEXT,
            office TEXT,
            start_date DATE,
            end_date DATE,
            final_period_end_date DATE,
            final_period_start_date DATE,
            search_tab INTEGER,
            provinces JSON,
            applicants JSON,
            communities JSON,
            action_items JSON,
            origins JSON,
            activities JSON,
            region_types JSON,
            types JSON,
            details JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        try:
            conn = mysql.connector.connect(**self.config.__dict__)
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Tabla funds creada exitosamente")
        except Exception as e:
            logger.error(f"Error creando la tabla funds: {str(e)}")
            raise

    def _create_indexes(self):
        """Crear los índices"""
        try:
            conn = mysql.connector.connect(**self.config.__dict__)
            cursor = conn.cursor()
            
            # Primero verificamos si los índices existen
            cursor.execute("""
                SELECT INDEX_NAME 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'funds'
            """, (self.config.database,))
            
            existing_indexes = [row[0] for row in cursor.fetchall()]
            
            # Crear índices si no existen
            if 'idx_fund_is_open' not in existing_indexes:
                cursor.execute("CREATE INDEX idx_fund_is_open ON funds(is_open)")
                logger.info("Índice idx_fund_is_open creado")
                
            if 'idx_fund_dates' not in existing_indexes:
                cursor.execute("CREATE INDEX idx_fund_dates ON funds(start_date, end_date)")
                logger.info("Índice idx_fund_dates creado")
                
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Proceso de creación de índices completado")
        except Exception as e:
            logger.error(f"Error creando los índices: {str(e)}")
            raise

def main():
    try:
        config = DatabaseConfig()
        db_setup = DatabaseSetup(config)
        db_setup.setup_database()
        logger.info("Configuración de base de datos completada exitosamente")
    except Exception as e:
        logger.error(f"Error en la configuración de la base de datos: {str(e)}")
        raise

if __name__ == "__main__":
    main()