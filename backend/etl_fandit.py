import requests
import json
import mysql.connector
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    filename='fandit_etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración
FANDIT_API_URL = "https://sandbox.api.test.fandit.es/api/v2"
EXPERT_TOKEN = os.getenv("FANDIT_EXPERT_TOKEN")

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv("AURORA_CLUSTER_ENDPOINT"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': 'fandit_db'
}

def get_api_data(endpoint):
    """
    Obtiene datos de la API de Fandit
    """
    headers = {
        'Authorization': f'Bearer {EXPERT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{FANDIT_API_URL}/{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener datos de la API para {endpoint}: {str(e)}")
        raise

def save_funds_data(data):
    """
    Guarda los datos en la tabla funds
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for fund in data:
            # Convertir listas/diccionarios a JSON strings
            applicants = json.dumps(fund.get('applicants', []))
            action_items = json.dumps(fund.get('action_items', []))
            origins = json.dumps(fund.get('origins', []))
            activities = json.dumps(fund.get('activities', []))
            region_types = json.dumps(fund.get('region_types', []))
            types = json.dumps(fund.get('types', []))

            # Preparar la consulta SQL
            sql = """
            INSERT INTO funds (
                title, is_open, max_budget, bdns, office, 
                publication_date, end_date, search_tab,
                applicants, action_items, origins, activities,
                region_types, types
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                is_open = VALUES(is_open),
                max_budget = VALUES(max_budget),
                bdns = VALUES(bdns),
                office = VALUES(office),
                publication_date = VALUES(publication_date),
                end_date = VALUES(end_date),
                search_tab = VALUES(search_tab),
                applicants = VALUES(applicants),
                action_items = VALUES(action_items),
                origins = VALUES(origins),
                activities = VALUES(activities),
                region_types = VALUES(region_types),
                types = VALUES(types)
            """
            
            values = (
                fund.get('title'),
                fund.get('is_open'),
                fund.get('max_budget'),
                fund.get('bdns'),
                fund.get('office'),
                fund.get('publication_date'),
                fund.get('end_date'),
                fund.get('search_tab'),
                applicants,
                action_items,
                origins,
                activities,
                region_types,
                types
            )

            cursor.execute(sql, values)

        conn.commit()
        logger.info("Datos guardados exitosamente en la tabla funds")

    except mysql.connector.Error as e:
        logger.error(f"Error al guardar datos en funds: {str(e)}")
        raise
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def save_fund_details_data(data):
    """
    Guarda los datos en la tabla fund_details
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for detail in data:
            # Convertir campos JSON
            official_info = json.dumps(detail.get('official_info', {}))
            eligible_recipients = json.dumps(detail.get('eligible_recipients', []))
            covered_expenses = json.dumps(detail.get('covered_expenses', []))
            additional_info = json.dumps(detail.get('additional_info', {}))

            sql = """
            INSERT INTO fund_details (
                title, purpose, submission_period_opening,
                submission_period_closing, funds, scope, max_aid,
                official_info, eligible_recipients,
                covered_expenses, additional_info
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                purpose = VALUES(purpose),
                submission_period_opening = VALUES(submission_period_opening),
                submission_period_closing = VALUES(submission_period_closing),
                funds = VALUES(funds),
                scope = VALUES(scope),
                max_aid = VALUES(max_aid),
                official_info = VALUES(official_info),
                eligible_recipients = VALUES(eligible_recipients),
                covered_expenses = VALUES(covered_expenses),
                additional_info = VALUES(additional_info)
            """

            values = (
                detail.get('title'),
                detail.get('purpose'),
                detail.get('submission_period_opening'),
                detail.get('submission_period_closing'),
                detail.get('funds'),
                detail.get('scope'),
                detail.get('max_aid'),
                official_info,
                eligible_recipients,
                covered_expenses,
                additional_info
            )

            cursor.execute(sql, values)

        conn.commit()
        logger.info("Datos guardados exitosamente en la tabla fund_details")

    except mysql.connector.Error as e:
        logger.error(f"Error al guardar datos en fund_details: {str(e)}")
        raise
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def main():
    """
    Función principal que ejecuta el proceso ETL
    """
    try:
        # Obtener y guardar datos de funds
        funds_data = get_api_data('funds')
        save_funds_data(funds_data)
        
        # Obtener y guardar datos de fund_details
        fund_details_data = get_api_data('fund_details')
        save_fund_details_data(fund_details_data)
        
        logger.info("Proceso ETL completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en el proceso ETL: {str(e)}")
        raise

if __name__ == "__main__":
    main()