import requests
import psycopg2
from datetime import datetime
import schedule
import time
import os
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
import json

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fandit_etl.log'),
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

class FanditAPI:
    def __init__(self, expert_token: str, api_key: str, base_url: str = os.getenv('FANDIT_BASE_URL')):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'ExpertToken {expert_token}',
            'api-key': api_key
        })
        logger.info("API inicializada")

    def get_funds(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de fondos con parámetros opcionales de filtrado"""
        try:
            # Parámetros por defecto para la búsqueda
            default_params = {
                "is_open": True,
                "search_by_text": None,
                "max_budget": None,
                "max_total_amount": None,
                "min_total_amount": None,
                "bdns": None,
                "office": "",
                "start_date": datetime.now().strftime("%Y-01-01"),
                "end_date": datetime.now().strftime("%Y-12-31"),
                "final_period_end_date": datetime.now().strftime("%Y-12-31"),
                "final_period_start_date": datetime.now().strftime("%Y-01-01"),
                "search_tab": None,
                "provinces": [],
                "applicants": [],
                "communities": [],
                "action_items": [],
                "origins": [],
                "activities": [],
                "region_types": [],
                "types": []
            }

            if params:
                default_params.update(params)

            query_params = {
                "page": 1,
                "requestData": json.dumps(default_params)
            }

            logger.info("Realizando petición a la API de Fandit")
            response = self.session.get(
                f"{self.base_url}/funds/",
                params=query_params
            )
            
            logger.info(f"Status code: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])  # Asumimos que la respuesta tiene una key 'results'
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a la API: {str(e)}")
            raise

class PostgresDB:
    CREATE_FUNDS_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS funds (
            id SERIAL PRIMARY KEY,
            fund_id VARCHAR(255) UNIQUE,
            is_open BOOLEAN,
            search_by_text TEXT,
            max_budget NUMERIC,
            max_total_amount NUMERIC,
            min_total_amount NUMERIC,
            bdns TEXT,
            office TEXT,
            start_date DATE,
            end_date DATE,
            final_period_end_date DATE,
            final_period_start_date DATE,
            search_tab INTEGER,
            provinces TEXT[],
            applicants TEXT[],
            communities TEXT[],
            action_items TEXT[],
            origins TEXT[],
            activities TEXT[],
            region_types TEXT[],
            types TEXT[],
            details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_fund_is_open ON funds(is_open);
        CREATE INDEX IF NOT EXISTS idx_fund_dates ON funds(start_date, end_date);
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._create_database_if_not_exists()
        self.create_tables()

    def _create_database_if_not_exists(self):
        """Crear la base de datos si no existe"""
        try:
            # Conectar a postgres para poder crear la base de datos
            conn = psycopg2.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                database='postgres'
            )
            conn.autocommit = True

            with conn.cursor() as cur:
                # Verificar si la base de datos existe
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.config.database,))
                if not cur.fetchone():
                    cur.execute(f'CREATE DATABASE {self.config.database}')
                    logger.info(f"Base de datos {self.config.database} creada")
            conn.close()
        except Exception as e:
            logger.error(f"Error creando la base de datos: {str(e)}")
            raise

    def create_tables(self):
        """Crear las tablas necesarias"""
        try:
            conn = psycopg2.connect(**self.config.__dict__)
            with conn:
                with conn.cursor() as cur:
                    cur.execute(self.CREATE_FUNDS_TABLE_SQL)
            conn.close()
            logger.info("Tablas creadas exitosamente")
        except Exception as e:
            logger.error(f"Error creando las tablas: {str(e)}")
            raise

    def upsert_fund(self, fund: Dict, details: Dict):
        """Insertar o actualizar un fondo en la base de datos"""
        upsert_query = """
        INSERT INTO funds (
            fund_id, is_open, search_by_text, max_budget, max_total_amount,
            min_total_amount, bdns, office, start_date, end_date,
            final_period_end_date, final_period_start_date, search_tab,
            provinces, applicants, communities, action_items,
            origins, activities, region_types, types, details,
            updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (fund_id) DO UPDATE SET
            is_open = EXCLUDED.is_open,
            search_by_text = EXCLUDED.search_by_text,
            max_budget = EXCLUDED.max_budget,
            max_total_amount = EXCLUDED.max_total_amount,
            min_total_amount = EXCLUDED.min_total_amount,
            bdns = EXCLUDED.bdns,
            office = EXCLUDED.office,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            final_period_end_date = EXCLUDED.final_period_end_date,
            final_period_start_date = EXCLUDED.final_period_start_date,
            search_tab = EXCLUDED.search_tab,
            provinces = EXCLUDED.provinces,
            applicants = EXCLUDED.applicants,
            communities = EXCLUDED.communities,
            action_items = EXCLUDED.action_items,
            origins = EXCLUDED.origins,
            activities = EXCLUDED.activities,
            region_types = EXCLUDED.region_types,
            types = EXCLUDED.types,
            details = EXCLUDED.details,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        try:
            with psycopg2.connect(**self.config.__dict__) as conn:
                with conn.cursor() as cur:
                    values = (
                        fund.get('id'),
                        fund.get('is_open'),
                        fund.get('search_by_text'),
                        fund.get('max_budget'),
                        fund.get('max_total_amount'),
                        fund.get('min_total_amount'),
                        fund.get('bdns'),
                        fund.get('office'),
                        fund.get('start_date'),
                        fund.get('end_date'),
                        fund.get('final_period_end_date'),
                        fund.get('final_period_start_date'),
                        fund.get('search_tab'),
                        fund.get('provinces', []),
                        fund.get('applicants', []),
                        fund.get('communities', []),
                        fund.get('action_items', []),
                        fund.get('origins', []),
                        fund.get('activities', []),
                        fund.get('region_types', []),
                        fund.get('types', []),
                        json.dumps(details)
                    )
                    cur.execute(upsert_query, values)
            logger.info(f"Fondo {fund.get('id')} procesado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando fondo: {str(e)}")
            raise

class FanditETL:
    def __init__(self, api: FanditAPI):
        self.api = api
        self.db = PostgresDB(DatabaseConfig())
        logger.info("ETL inicializado")

    def run_etl(self):
        """Ejecutar el proceso ETL completo"""
        try:
            logger.info("Iniciando proceso ETL")
            funds = self.api.get_funds()
            
            if not funds:
                logger.warning("No se encontraron fondos")
                return

            logger.info(f"Procesando {len(funds)} fondos")
            for fund in funds:
                try:
                    self.db.upsert_fund(fund, fund)
                except Exception as e:
                    logger.error(f"Error procesando fondo: {str(e)}")
                    continue
                time.sleep(0.5)  # Evitar sobrecarga de la API
                
            logger.info("Proceso ETL completado")
        except Exception as e:
            logger.error(f"Error en el proceso ETL: {str(e)}")
            raise

def main():
    try:
        # Cargar credenciales
        expert_token = os.getenv('FANDIT_EXPERT_TOKEN')
        api_key = os.getenv('FANDIT_API_KEY')

        if not all([expert_token, api_key]):
            raise ValueError("Faltan credenciales de la API en las variables de entorno")

        # Inicializar servicios
        api = FanditAPI(expert_token=expert_token, api_key=api_key)
        etl = FanditETL(api)
        
        # Ejecutar ETL
        logger.info("Iniciando servicio ETL")
        etl.run_etl()
        
        # Programar ejecución diaria
        schedule.every().day.at("13:00").do(etl.run_etl)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    except Exception as e:
        logger.error(f"Error en la aplicación: {str(e)}")
        raise

if __name__ == "__main__":
    main()