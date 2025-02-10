import mysql.connector
import os
import json
from dotenv import load_dotenv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def connect_to_database():
    """Establecer conexión a la base de datos"""
    conn = mysql.connector.connect(
        host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database='fandit_db'
    )
    return conn

def load_fund_details():
    """Cargar datos de grants_detail.json"""
    conn = connect_to_database()
    cursor = conn.cursor()

    # Cargar datos de grants_detail.json
    with open('grants_detail.json', 'r', encoding='utf-8') as f:
        grants_detail = json.load(f)

    # Limpiar tabla existente antes de insertar
    cursor.execute("DELETE FROM fund_details")

    # Insertar datos detallados de subvenciones
    for grant in grants_detail['grants']:
        cursor.execute("""
        INSERT INTO fund_details 
        (title, purpose, 
        submission_period_opening, submission_period_closing, 
        funds, scope, max_aid, 
        official_info, eligible_recipients, 
        covered_expenses, additional_info)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            grant.get('title'),
            grant.get('purpose'),
            # Convertir fechas si están presentes
            datetime.strptime(grant.get('submission_period', {}).get('opening'), '%d/%m/%Y') 
                if grant.get('submission_period', {}).get('opening') else None,
            datetime.strptime(grant.get('submission_period', {}).get('closing'), '%d/%m/%Y') 
                if grant.get('submission_period', {}).get('closing') else None,
            grant.get('funds'),
            grant.get('scope'),
            grant.get('max_aid'),
            json.dumps(grant.get('official_info', {})),
            json.dumps(grant.get('eligible_recipients', {})),
            json.dumps(grant.get('covered_expenses', [])),
            json.dumps(grant.get('additional_info', []))
        ))

    conn.commit()
    cursor.close()
    conn.close()

    logger.info("Datos insertados exitosamente en la tabla fund_details")

def main():
    load_fund_details()

if __name__ == "__main__":
    main()