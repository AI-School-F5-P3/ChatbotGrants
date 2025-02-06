import requests
from datetime import datetime
import schedule
import time
import os
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
import json
import mysql.connector

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl.log'),
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
            return data.get('results', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a la API: {str(e)}")
            raise

class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def upsert_fund(self, fund: Dict, details: Dict):
        """Insertar o actualizar un fondo en la base de datos"""
        upsert_query = """
        INSERT INTO funds (
            fund_id, is_open, search_by_text, max_budget, max_total_amount,
            min_total_amount, bdns, office, start_date, end_date,
            final_period_end_date, final_period_start_date, search_tab,
            provinces, applicants, communities, action_items,
            origins, activities, region_types, types, details
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            is_open = VALUES(is_open),
            search_by_text = VALUES(search_by_text),
            max_budget = VALUES(max_budget),
            max_total_amount = VALUES(max_total_amount),
            min_total_amount = VALUES(min_total_amount),
            bdns = VALUES(bdns),
            office = VALUES(office),
            start_date = VALUES(start_date),
            end_date = VALUES(end_date),
            final_period_end_date = VALUES(final_period_end_date),
            final_period_start_date = VALUES(final_period_start_date),
            search_tab = VALUES(search_tab),
            provinces = VALUES(provinces),
            applicants = VALUES(applicants),
            communities = VALUES(communities),
            action_items = VALUES(action_items),
            origins = VALUES(origins),
            activities = VALUES(activities),
            region_types = VALUES(region_types),
            types = VALUES(types),
            details = VALUES(details)
        """
        try:
            conn = mysql.connector.connect(**self.config.__dict__)
            cursor = conn.cursor()
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
                json.dumps(fund.get('provinces', [])),
                json.dumps(fund.get('applicants', [])),
                json.dumps(fund.get('communities', [])),
                json.dumps(fund.get('action_items', [])),
                json.dumps(fund.get('origins', [])),
                json.dumps(fund.get('activities', [])),
                json.dumps(fund.get('region_types', [])),
                json.dumps(fund.get('types', [])),
                json.dumps(details)
            )
            cursor.execute(upsert_query, values)
            conn.commit()
            conn.close()
            logger.info(f"Fondo {fund.get('id')} procesado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando fondo: {str(e)}")
            raise

class FanditETL:
    def __init__(self, api: FanditAPI):
        self.api = api
        self.db = DatabaseManager(DatabaseConfig())
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
                time.sleep(0.5)
                
            logger.info("Proceso ETL completado")
        except Exception as e:
            logger.error(f"Error en el proceso ETL: {str(e)}")
            raise

def main():
    try:
        expert_token = os.getenv('FANDIT_EXPERT_TOKEN')
        api_key = os.getenv('FANDIT_API_KEY')

        if not all([expert_token, api_key]):
            raise ValueError("Faltan credenciales de la API en las variables de entorno")

        api = FanditAPI(expert_token=expert_token, api_key=api_key)
        etl = FanditETL(api)
        
        logger.info("Iniciando servicio ETL")
        etl.run_etl()
        
        schedule.every().day.at("13:00").do(etl.run_etl)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    except Exception as e:
        logger.error(f"Error en la aplicación: {str(e)}")
        raise

if __name__ == "__main__":
    main()