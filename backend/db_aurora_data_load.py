import mysql.connector
import os
import json
from dotenv import load_dotenv
import logging

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

def create_tables():
    """Crear tablas si no existen"""
    conn = connect_to_database()
    cursor = conn.cursor()

    # Tabla para búsqueda de subvenciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funds (
        id INT AUTO_INCREMENT PRIMARY KEY,
        is_open BOOLEAN,
        title VARCHAR(255),
        description TEXT,
        max_budget DECIMAL(15,2),
        total_amount DECIMAL(15,2),
        min_total_amount DECIMAL(15,2),
        bdns VARCHAR(50),
        office VARCHAR(255),
        publication_date DATE,
        end_date DATE,
        search_tab INT,
        applicants JSON,
        action_items JSON,
        origins JSON,
        activities JSON,
        region_types JSON,
        types JSON
    )
    """)

    # Tabla para detalles detallados de subvenciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fund_details (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        purpose TEXT,
        submission_period_opening DATE,
        submission_period_closing DATE,
        funds VARCHAR(100),
        scope VARCHAR(100),
        max_aid VARCHAR(50),
        official_info JSON,
        eligible_recipients JSON,
        covered_expenses JSON,
        additional_info JSON
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def load_grants_data():
    """Cargar datos de grants_search.json y grants_detail.json"""
    conn = connect_to_database()
    cursor = conn.cursor()

    # Cargar datos de grants_search.json
    with open('grants_search.json', 'r', encoding='utf-8') as f:
        funds = json.load(f)

    # Cargar datos de grants_detail.json
    with open('grants_detail.json', 'r', encoding='utf-8') as f:
        fund_details = json.load(f)

    # Limpiar tablas existentes antes de insertar
    cursor.execute("DELETE FROM funds")
    cursor.execute("DELETE FROM fund_details")

    # Insertar datos de búsqueda de subvenciones
    for grant in funds['grants']:
        cursor.execute("""
        INSERT INTO funds
        (is_open, title, description, max_budget, total_amount, min_total_amount, 
        bdns, office, publication_date, end_date, search_tab, 
        applicants, action_items, origins, activities, region_types, types)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            grant.get('is_open'), 
            grant.get('title'), 
            grant.get('description'), 
            grant.get('max_budget'), 
            grant.get('total_amount'), 
            grant.get('min_total_amount'),
            grant.get('bdns'),
            grant.get('office'),
            grant.get('publication_date'),
            grant.get('end_date'),
            grant.get('search_tab'),
            json.dumps(grant.get('applicants', [])),
            json.dumps(grant.get('action_items', [])),
            json.dumps(grant.get('origins', [])),
            json.dumps(grant.get('activities', [])),
            json.dumps(grant.get('region_types', [])),
            json.dumps(grant.get('types', []))
        ))

    # Insertar datos detallados de subvenciones
    for grant in fund_details['grants']:
        cursor.execute("""
        INSERT INTO fund_details 
        (title, purpose, submission_period_opening, submission_period_closing, 
        funds, scope, max_aid, official_info, eligible_recipients, 
        covered_expenses, additional_info)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            grant.get('title'),
            grant.get('purpose'),
            grant.get('submission_period', {}).get('opening'),
            grant.get('submission_period', {}).get('closing'),
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

    logger.info("Datos insertados exitosamente")

def main():
    create_tables()
    load_grants_data()

if __name__ == "__main__":
    main()