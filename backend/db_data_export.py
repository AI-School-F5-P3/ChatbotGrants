import mysql.connector
import csv
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def connect_db():
    """Establece conexión con la base de datos Aurora"""
    return mysql.connector.connect(
        host=os.getenv('AURORA_CLUSTER_ENDPOINT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database='fandit_db'
    )

def get_table_data(cursor: mysql.connector.cursor.MySQLCursor, table: str) -> tuple[List[str], List[Dict]]:
    """
    Obtiene los datos de una tabla específica
    Returns: (columnas, datos)
    """
    try:
        # Obtener columnas
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [column[0] for column in cursor.fetchall()]
        
        # Obtener datos
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Convertir a lista de diccionarios
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Convertir campos JSON
            for key, value in row_dict.items():
                if isinstance(value, bytes):
                    try:
                        row_dict[key] = json.loads(value.decode('utf-8'))
                    except:
                        row_dict[key] = value.decode('utf-8')
            data.append(row_dict)
            
        return columns, data
    
    except Exception as e:
        logger.error(f"Error obteniendo datos de {table}: {str(e)}")
        raise

def export_to_csv(data: List[Dict], columns: List[str], filename: str):
    """Exporta los datos a un archivo CSV"""
    try:
        # Crear directorio de salida si no existe
        output_dir = "exports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for row in data:
                # Convertir campos JSON a string
                row_copy = row.copy()
                for key, value in row_copy.items():
                    if isinstance(value, (dict, list)):
                        row_copy[key] = json.dumps(value, ensure_ascii=False)
                writer.writerow(row_copy)
                
        logger.info(f"Archivo exportado exitosamente: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error exportando a CSV {filename}: {str(e)}")
        raise

def main():
    """Función principal para exportar los datos"""
    try:
        logger.info("Iniciando proceso de exportación")
        
        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor()
        
        # Timestamp para los archivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Exportar funds
        logger.info("Exportando tabla funds...")
        funds_columns, funds_data = get_table_data(cursor, 'funds')
        funds_file = export_to_csv(
            funds_data, 
            funds_columns, 
            f"funds_{timestamp}.csv"
        )
        logger.info(f"Exportados {len(funds_data)} registros de funds")
        
        # Exportar fund_details
        logger.info("Exportando tabla fund_details...")
        details_columns, details_data = get_table_data(cursor, 'fund_details')
        details_file = export_to_csv(
            details_data, 
            details_columns, 
            f"fund_details_{timestamp}.csv"
        )
        logger.info(f"Exportados {len(details_data)} registros de fund_details")
        
        logger.info("Proceso de exportación completado exitosamente")
        logger.info(f"Archivos generados:\n- {funds_file}\n- {details_file}")
        
    except Exception as e:
        logger.error(f"Error en el proceso de exportación: {str(e)}")
        raise
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            logger.info("Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()