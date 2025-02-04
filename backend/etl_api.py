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
    def __init__(self, base_url: str = 'https://fandit.es/api/business', api_key: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configurar headers por defecto
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'ChatbotGrants/1.0'
        })
        
        # Si hay API key, agregarla a los headers
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
            
        # Verificar conectividad con la API
        try:
            response = self.session.get(f"{self.base_url}/health")  # O cualquier endpoint de health check
            logger.info(f"Conexión a API exitosa. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"No se pudo verificar la conexión a la API: {str(e)}")
        
    def get_funds(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de fondos con parámetros opcionales de filtrado"""
        try:
            response = self.session.get(f"{self.base_url}/funds", params=params)
            logger.info(f"URL de la petición: {response.url}")
            logger.info(f"Código de estado: {response.status_code}")
            logger.info(f"Headers de respuesta: {response.headers}")
            
            # Log del contenido de la respuesta
            logger.info(f"Contenido de la respuesta: {response.text[:500]}...")  # Primeros 500 caracteres
            
            response.raise_for_status()  # Esto lanzará una excepción si el status code no es 2XX
            
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Error decodificando JSON: {str(e)}")
                logger.error(f"Respuesta completa: {response.text}")
                raise
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a la API de Fandit: {str(e)}")
            logger.error(f"Detalles de la petición: URL={self.base_url}/funds, params={params}")
            raise

        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            logger.error(f"Tipo de error: {type(e)}")
            raise

    def get_fund_details(self, fund_id: str) -> Dict:
        """Obtener detalles específicos de un fondo"""
        try:
            response = self.session.get(f"{self.base_url}/funds/{fund_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo detalles del fondo {fund_id}: {str(e)}")
            raise

class PostgresDB:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.create_tables()

    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        create_funds_table = """
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
        
        try:
            with psycopg2.connect(**self.config.__dict__) as conn:
                with conn.cursor() as cur:
                    cur.execute(create_funds_table)
                conn.commit()
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
    def __init__(self):
        self.api = FanditAPI()
        self.db = PostgresDB(DatabaseConfig())
        
    def run_etl(self):
        """Ejecutar el proceso ETL completo"""
        try:
            logger.info("Iniciando proceso ETL")
            
            # Obtener solo convocatorias abiertas
            funds = self.api.get_funds(params={'is_open': True})
            
            for fund in funds:
                # Obtener detalles adicionales de cada fondo
                fund_details = self.api.get_fund_details(fund['id'])
                # Almacenar en la base de datos
                self.db.upsert_fund(fund, fund_details)
                
                # Dormir brevemente para no sobrecargar la API
                time.sleep(1)
            
            logger.info(f"Proceso ETL completado exitosamente. Actualizados {len(funds)} fondos")
        except Exception as e:
            logger.error(f"Error en el proceso ETL: {str(e)}")

def main():
    """Función principal que configura y ejecuta el ETL programado"""
    etl = FanditETL()
    
    # Programar la ejecución diaria a las 13:00
    schedule.every().day.at("13:00").do(etl.run_etl)
    
    logger.info("Iniciando el servicio ETL")
    
    # Ejecutar inmediatamente la primera vez
    etl.run_etl()
    
    # Mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()