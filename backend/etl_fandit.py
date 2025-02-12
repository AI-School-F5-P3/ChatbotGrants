import asyncio
import json
import mysql.connector
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
from dotenv import load_dotenv
from clase_apifandit import FanditAPI
import pytz

def setup_logging():
    """
    Configura el sistema de logging con rotación de archivos y formato detallado
    """
    log_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] - '
        'Operation: %(operation)s - '
        'Entity: %(entity)s - '
        'Details: %(message)s'
    )

    # Configurar el manejador de archivos con rotación
    file_handler = RotatingFileHandler(
        'fandit_etl.log',
        maxBytes=10*1024*1024,  # 10MB por archivo
        backupCount=5  # Mantener 5 archivos de respaldo
    )
    file_handler.setFormatter(log_formatter)

    # Configurar el manejador de consola para debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Configurar el logger
    logger = logging.getLogger('fandit_etl')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Configuración global
load_dotenv()
logger = setup_logging()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv("AURORA_CLUSTER_ENDPOINT"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': 'fandit_db'
}

# Inicializar API Fandit
api = FanditAPI(
    token=os.getenv("FANDIT_TOKEN"),
    expert_token=os.getenv("FANDIT_EXPERT_TOKEN")
)

async def get_all_funds():
    """
    Obtiene todas las subvenciones disponibles de la API
    """
    try:
        request_data = {
            "is_open": None,
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
        
        logger.info(
            "Iniciando obtención de subvenciones",
            extra={'operation': 'api_request', 'entity': 'funds'}
        )
        
        response = await api.obtener_lista_subvenciones(page=1, request_data=request_data)
        
        logger.info(
            f"Obtenidas {len(response.get('results', []))} subvenciones",
            extra={'operation': 'api_response', 'entity': 'funds'}
        )
        
        return response
    except Exception as e:
        logger.error(
            f"Error obteniendo subvenciones: {str(e)}",
            extra={'operation': 'api_error', 'entity': 'funds'}
        )
        raise

def update_fund(cursor, fund_data):
    """
    Actualiza o inserta un registro de fund comparando todos los campos
    """
    slug = fund_data.get('slug', '')
    
    try:
        # Obtener registro actual si existe
        check_sql = "SELECT * FROM funds WHERE slug = %s"
        cursor.execute(check_sql, (slug,))
        columns = [desc[0] for desc in cursor.description]
        result = cursor.fetchone()
        
        if result:
            # Comparar y actualizar campos modificados
            current_data = dict(zip(columns, result))
            new_data = {
                'title': fund_data.get('formatted_title'),
                'is_open': 1 if "abierta" in fund_data.get('status_text', '').lower() else 0,
                'max_budget': fund_data.get('total_amount', 0.0),
                'bdns': fund_data.get('bdns'),
                'office': fund_data.get('entity'),
                'publication_date': fund_data.get('publication_date'),
                'end_date': fund_data.get('end_date'),
                'search_tab': fund_data.get('search_tab', 0),
                'provinces': json.dumps(fund_data.get('provinces', [])),
                'communities': json.dumps(fund_data.get('communities', [])),
                'applicants': json.dumps(fund_data.get('applicants', [])),
                'action_items': json.dumps(fund_data.get('action_items', [])),
                'origins': json.dumps(fund_data.get('origins', [])),
                'activities': json.dumps(fund_data.get('activities', [])),
                'region_types': json.dumps(fund_data.get('region_types', [])),
                'types': json.dumps(fund_data.get('types', []))
            }
            
            # Detectar cambios
            changes = []
            update_fields = []
            update_values = []
            
            for field, new_value in new_data.items():
                current_value = current_data.get(field)
                
                # Convertir bytes a string para comparación
                if isinstance(current_value, bytes):
                    current_value = current_value.decode('utf-8')
                
                if new_value != current_value:
                    update_fields.append(f"{field} = %s")
                    update_values.append(new_value)
                    changes.append({
                        'field': field,
                        'old': current_value,
                        'new': new_value
                    })
            
            if changes:
                # Actualizar registro
                update_sql = f"""
                UPDATE funds SET 
                    {', '.join(update_fields)},
                    updated_at = NOW()
                WHERE slug = %s
                """
                update_values.append(slug)
                cursor.execute(update_sql, tuple(update_values))
                
                # Registrar cada cambio en el log
                for change in changes:
                    logger.info(
                        f"Campo '{change['field']}' cambió de '{change['old']}' a '{change['new']}'",
                        extra={
                            'operation': 'update',
                            'entity': f'funds/{slug}'
                        }
                    )
                
                return True
            
            logger.info(
                "No se detectaron cambios",
                extra={'operation': 'check', 'entity': f'funds/{slug}'}
            )
            return False
            
        else:
            # Insertar nuevo registro
            columns = ', '.join([
                'slug', 'title', 'is_open', 'max_budget', 'bdns', 'office',
                'publication_date', 'end_date', 'search_tab', 'provinces',
                'communities', 'applicants', 'action_items', 'origins',
                'activities', 'region_types', 'types'
            ])
            placeholders = ', '.join(['%s'] * 17)
            
            insert_sql = f"""
            INSERT INTO funds ({columns})
            VALUES ({placeholders})
            """
            
            values = (
                slug,
                fund_data.get('formatted_title'),
                1 if "abierta" in fund_data.get('status_text', '').lower() else 0,
                fund_data.get('total_amount', 0.0),
                fund_data.get('bdns'),
                fund_data.get('entity'),
                fund_data.get('publication_date'),
                fund_data.get('end_date'),
                fund_data.get('search_tab', 0),
                json.dumps(fund_data.get('provinces', [])),
                json.dumps(fund_data.get('communities', [])),
                json.dumps(fund_data.get('applicants', [])),
                json.dumps(fund_data.get('action_items', [])),
                json.dumps(fund_data.get('origins', [])),
                json.dumps(fund_data.get('activities', [])),
                json.dumps(fund_data.get('region_types', [])),
                json.dumps(fund_data.get('types', []))
            )
            
            cursor.execute(insert_sql, values)
            
            logger.info(
                f"Nueva subvención creada",
                extra={
                    'operation': 'insert',
                    'entity': f'funds/{slug}'
                }
            )
            return True
            
    except Exception as e:
        logger.error(
            f"Error procesando subvención: {str(e)}",
            extra={
                'operation': 'error',
                'entity': f'funds/{slug}'
            }
        )
        raise

async def main():
    """
    Función principal que ejecuta el proceso ETL
    """
    try:
             
        logger.info(
            "Iniciando proceso ETL",
            extra={
                'operation': 'start',
                'entity': 'etl'
            }
        )
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        try:
            # Obtener y procesar datos
            funds_data = await get_all_funds()
            if funds_data and 'results' in funds_data:
                updates = 0
                for fund in funds_data['results']:
                    if update_fund(cursor, fund):
                        updates += 1
                
                conn.commit()
                logger.info(
                    f"Proceso completado: {updates} registros actualizados",
                    extra={
                        'operation': 'complete',
                        'entity': 'etl'
                    }
                )
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(
            f"Error en proceso ETL: {str(e)}",
            extra={
                'operation': 'error',
                'entity': 'etl'
            }
        )
        raise

if __name__ == "__main__":
    asyncio.run(main())