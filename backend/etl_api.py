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
    host: str = os.getenv('DB_HOST', 'localhost')
    database: str = os.getenv('DB_NAME', 'fandit_db')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', '')
    port: str = os.getenv('DB_PORT', '5432')

class FanditAPI:
    def __init__(self, token: str, api_key: str = "2f8abdf6-0b87-4502-9c1d-79c52794e3fc", base_url: str = "https://sandbox.api.test.fandit.es/api/v2"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'ExpertToken {token}',  # Cambiado a ExpertToken
            'api-key': api_key,
            'Content-Type': 'application/json'  # Agregado Content-Type
        })
        logger.info(f"Headers configurados: {self.session.headers}")

    def get_funds(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de fondos con parámetros opcionales de filtrado"""
        try:
            # Parámetros por defecto
            default_params = {
                "is_open": True,
                "search_by_text": None,
                "max_budget": None,
                "max_total_amount": None,
                "min_total_amount": None,
                "bdns": None,
                "office": "",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "final_period_end_date": "2024-12-31",
                "final_period_start_date": "2024-01-01",
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

            # Actualizar con parámetros proporcionados
            if params:
                default_params.update(params)

            # Construir URL con parámetros
            query_params = {
                "page": 1,
                "requestData": json.dumps(default_params)
            }

            logger.info(f"Realizando petición a {self.base_url}/funds/")
            logger.info(f"Parámetros: {query_params}")

            response = self.session.get(
                f"{self.base_url}/funds/",
                params=query_params
            )
            
            logger.info(f"URL completa: {response.url}")
            logger.info(f"Status code: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Datos recibidos: {str(data)[:200]}...")  # Log primeros 200 caracteres
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a la API de Fandit: {str(e)}")
            if response := getattr(e, 'response', None):
                logger.error(f"Respuesta del servidor: {response.text}")
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
        self.create_tables()

    def create_tables(self):
        """Crear la base de datos si no existe y las tablas necesarias"""
        try:
            logger.info(f"Intentando conectar a la base de datos en {self.config.host}")
            conn = psycopg2.connect(**self.config.__dict__)
            logger.info("Conexión exitosa a la base de datos")
            
            with conn:
                with conn.cursor() as cur:
                    logger.info("Creando tablas...")
                    cur.execute(self.CREATE_FUNDS_TABLE_SQL)
                conn.commit()
            logger.info("Tablas creadas exitosamente")
        except Exception as e:
            logger.error(f"Error creando las tablas: {str(e)}")
            logger.error(f"Configuración de BD: {self.config}")
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
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        )
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
                conn.commit()
            logger.info(f"Fondo {fund.get('id')} actualizado exitosamente")
        except Exception as e:
            logger.error(f"Error actualizando el fondo {fund.get('id')}: {str(e)}")
            raise

class FanditETL:
    def __init__(self, api: FanditAPI):
        """
        Inicializa el ETL
        Args:
            api (FanditAPI): Instancia de la API de Fandit
        """
        self.api = api
        self.db = PostgresDB(DatabaseConfig())
        logger.info("FanditETL inicializado")

    def run_etl(self):
        """Ejecutar el proceso ETL completo"""
        try:
            logger.info("Iniciando proceso ETL")
            
            # Obtener fondos de la API
            funds = self.api.get_funds()
            
            if not funds:
                logger.warning("No se encontraron fondos")
                return

            logger.info(f"Obtenidos {len(funds)} fondos")
            
            # Almacenar cada fondo en la base de datos
            for fund in funds:
                try:
                    self.db.upsert_fund(fund, fund)
                    logger.info(f"Fondo {fund.get('id')} procesado exitosamente")
                except Exception as e:
                    logger.error(f"Error procesando fondo {fund.get('id')}: {str(e)}")
                    continue
                
                # Pequeña pausa para no sobrecargar la API
                time.sleep(0.5)
            
            logger.info("Proceso ETL completado exitosamente")
            
        except Exception as e:
            logger.error(f"Error en el proceso ETL: {str(e)}")
            raise

def main():
    """Función principal que configura y ejecuta el ETL programado"""
    load_dotenv()
    
    # Usar el token y api_key
    token = os.getenv('FANDIT_TOKEN', '4b7e374e04538b28b16e401108034eb6')
    api_key = os.getenv('FANDIT_API_KEY', '2f8abdf6-0b87-4502-9c1d-79c52794e3fc')
    
    # Inicializar API
    api = FanditAPI(token=token, api_key=api_key)
    
    # Inicializar ETL
    etl = FanditETL(api)
    
    logger.info("Iniciando el servicio ETL")
    
    # Ejecutar inmediatamente la primera vez
    etl.run_etl()
    
    # Programar la ejecución diaria a las 13:00
    schedule.every().day.at("13:00").do(etl.run_etl)
    
    # Mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
