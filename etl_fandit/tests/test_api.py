import asyncio
import json
import mysql.connector
import logging
import os
from dotenv import load_dotenv
from clase_apifandit import FanditAPI
from datetime import datetime
from typing import Dict, List, Any

# Configurar logging con más detalle
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_test_detailed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Definir los campos esperados de cada tabla
FUNDS_FIELDS = {
    'slug': 'slug',
    'title': 'formatted_title',
    'is_open': 'status_text',
    'max_budget': 'total_amount',
    'bdns': 'bdns',
    'office': 'entity',
    'publication_date': 'publication_date',
    'end_date': 'end_date',
    'final_period_start_date': 'final_period_start_date',
    'final_period_end_date': 'final_period_end_date',
    'search_tab': 'search_tab',
    'provinces': 'provinces',
    'communities': 'communities',
    'applicants': 'applicants',
    'action_items': 'action_items',
    'origins': 'origins',
    'activities': 'activities',
    'region_types': 'region_types',
    'types': 'types'
}

FUND_DETAILS_FIELDS = {
    'fund_slug': 'fund_slug',
    'title': 'title',
    'purpose': 'purpose',
    'submission_period_opening': 'submission_period_opening',
    'submission_period_closing': 'submission_period_closing',
    'funds': 'funds',
    'scope': 'scope',
    'max_aid': 'max_aid',
    'official_info': 'official_info',
    'eligible_recipients': 'eligible_recipients',
    'covered_expenses': 'covered_expenses',
    'additional_info': 'additional_info'
}

# Cargar variables de entorno y configurar API
load_dotenv()
api = FanditAPI(
    token=os.getenv("FANDIT_TOKEN"),
    expert_token=os.getenv("FANDIT_EXPERT_TOKEN")
)

def connect_db():
    """Establece conexión con la base de datos"""
    return mysql.connector.connect(
        host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database='fandit_db',
        charset='utf8mb4'
    )

async def get_sample_funds() -> List[Dict]:
    """Obtiene una muestra de subvenciones abiertas (máximo 3)"""
    try:
        request_data = {
            "is_open": True,
            "start_date": None,
            "end_date": None,
            "provinces": [],
            "applicants": [],
            "communities": [],
            "action_items": [],
            "origins": [],
            "activities": [],
            "region_types": [],
            "types": []
        }
        
        logger.info("Obteniendo muestra de subvenciones abiertas...")
        response = await api.obtener_lista_subvenciones(page=1, request_data=request_data)
        
        if not response or 'results' not in response:
            logger.error("No se obtuvieron resultados de la API")
            return []
        
        sample_funds = response['results'][:3]
        logger.info(f"Se obtuvieron {len(sample_funds)} subvenciones para análisis")
        
        # Verificar campos requeridos en cada subvención
        for fund in sample_funds:
            logger.info(f"\n=== Análisis de subvención: {fund.get('formatted_title', 'Sin título')} ===")
            logger.info(f"Estado: {fund.get('status_text', 'Sin estado')}")
            
            # Verificar todos los campos esperados
            logger.info("\nVerificación de campos requeridos para funds:")
            for db_field, api_field in FUNDS_FIELDS.items():
                value = fund.get(api_field)
                status = "✓ PRESENTE" if value is not None else "✗ AUSENTE"
                logger.info(f"{db_field} ({api_field}): {status}")
                if value is not None:
                    logger.info(f"  Valor: {value}")
        
        return sample_funds
        
    except Exception as e:
        logger.error(f"Error obteniendo subvenciones: {str(e)}")
        return []

async def get_fund_details(fund_slug: str) -> Dict:
    """Obtiene y verifica los detalles de una subvención específica"""
    try:
        logger.info(f"\nObteniendo detalles para slug: {fund_slug}")
        details = await api.obtener_detalle_subvencion(fund_slug)
        
        if details:
            logger.info("\nVerificación de campos requeridos para fund_details:")
            for db_field, api_field in FUND_DETAILS_FIELDS.items():
                value = details.get(api_field)
                status = "✓ PRESENTE" if value is not None else "✗ AUSENTE"
                logger.info(f"{db_field} ({api_field}): {status}")
                if value is not None:
                    logger.info(f"  Valor: {value}")
        else:
            logger.error(f"No se obtuvieron detalles para {fund_slug}")
            
        return details
        
    except Exception as e:
        logger.error(f"Error obteniendo detalles: {str(e)}")
        return {}

def analyze_field_mapping(api_data: Dict, table_name: str, fields_map: Dict) -> None:
    """Analiza y reporta el mapeo de campos entre la API y la base de datos"""
    logger.info(f"\n=== Análisis de mapeo para tabla {table_name} ===")
    
    # Campos presentes en la API pero no mapeados
    api_fields = set(api_data.keys())
    mapped_api_fields = set(fields_map.values())
    extra_fields = api_fields - mapped_api_fields
    if extra_fields:
        logger.info("\nCampos en la API no utilizados:")
        for field in extra_fields:
            logger.info(f"- {field}")
    
    # Campos requeridos pero no presentes en la API
    missing_fields = set()
    for db_field, api_field in fields_map.items():
        if api_field not in api_data:
            missing_fields.add(db_field)
    
    if missing_fields:
        logger.info("\nCampos requeridos no presentes en la API:")
        for field in missing_fields:
            logger.info(f"- {field}")

async def main():
    """Función principal de prueba"""
    try:
        logger.info("=== Iniciando prueba detallada de ETL ===")
        
        # 1. Obtener muestra de subvenciones
        sample_funds = await get_sample_funds()
        if not sample_funds:
            logger.error("No se obtuvieron subvenciones para probar")
            return
        
        # 2. Analizar cada subvención y sus detalles
        for fund in sample_funds:
            logger.info(f"\n=== Procesando subvención: {fund.get('formatted_title')} ===")
            
            # Analizar mapeo de campos para funds
            analyze_field_mapping(fund, 'funds', FUNDS_FIELDS)
            
            # Obtener y analizar detalles
            details = await get_fund_details(fund.get('slug'))
            if details:
                analyze_field_mapping(details, 'fund_details', FUND_DETAILS_FIELDS)
        
        logger.info("\n=== Prueba de ETL completada ===")
        
    except Exception as e:
        logger.error(f"Error en prueba de ETL: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())