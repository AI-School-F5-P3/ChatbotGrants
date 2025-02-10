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

def load_grants_data():
    """Cargar datos de grants_search.json"""
    conn = connect_to_database()
    cursor = conn.cursor()

    # Cargar datos de grants_search.json
    with open('grants_search.json', 'r', encoding='utf-8') as f:
        grants_search = json.load(f)

    # Limpiar tabla existente antes de insertar
    cursor.execute("DELETE FROM funds")

    # Insertar datos de búsqueda de subvenciones
    for grant in grants_search['grants']:
        cursor.execute("""
        INSERT INTO funds 
        (fund_id, name, description, total_amount, 
        is_open, max_budget, bdns, office, 
        publication_date, end_date, search_tab, 
        applicants, action_items, origins, activities, region_types, types)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f"GRANT-{grant.get('bdns')}", 
            grant.get('title'), 
            grant.get('description'), 
            grant.get('total_amount'), 
            grant.get('is_open'),
            grant.get('max_budget'), 
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

    conn.commit()
    cursor.close()
    conn.close()

    logger.info("Datos insertados exitosamente en la tabla funds")

def main():
    load_grants_data()

if __name__ == "__main__":
    main()