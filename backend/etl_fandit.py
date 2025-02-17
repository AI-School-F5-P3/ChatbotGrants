import asyncio
import json
import mysql.connector
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, date, time
import os
from dotenv import load_dotenv
from clase_apifandit import FanditAPI
import pytz
from typing import Dict, List, Any, Optional
from decimal import Decimal


# Mapeos para la transformación de datos
# Funciones auxiliares para el mapeo
def check_is_open(data):
    return 1 if "abierta" in data.get('status_text', '').lower() else 0

def get_nested_bdns(data):
    return data.get('info_extra', {}).get('bdns')

def get_start_date(data):
    return data.get('fund_execution_period', {}).get('start_date')

def get_end_date(data):
    return data.get('fund_execution_period', {}).get('end_date')

def get_final_start_date(data):
    return data.get('fund_execution_period', {}).get('final_start_date')

def get_final_end_date(data):
    return data.get('fund_execution_period', {}).get('final_end_date')

def get_search_tab(data):
    return data.get('search_tab', 0)

def get_provinces(data):
    return data.get('provinces', [])

def get_communities(data):
    return data.get('communities', [])

def get_applicants(data):
    return data.get('applicants', [])

def get_action_items(data):
    return data.get('action_items', [])

def get_origins(data):
    return data.get('origins', [])

def get_activities(data):
    return data.get('activities', [])

def get_region_types(data):
    return data.get('region_types', [])

def get_types(data):
    return data.get('types', [])

# Mapeos para la transformación de datos
FUNDS_MAPPING = {
    'slug': 'slug',
    'title': 'formatted_title',
    'is_open': check_is_open,
    'max_budget': 'total_amount',
    'bdns': get_nested_bdns,
    'office': 'entity',
    'publication_date': get_start_date,
    'end_date': get_end_date,
    'final_period_start_date': get_final_start_date,
    'final_period_end_date': get_final_end_date,
    'search_tab': get_search_tab,
    'provinces': get_provinces,
    'communities': get_communities,
    'applicants': get_applicants,
    'action_items': get_action_items,
    'origins': get_origins,
    'activities': get_activities,
    'region_types': get_region_types,
    'types': get_types
}

def get_submission_start(data):
    return data.get('fund_execution_period', {}).get('submission_start')

def get_submission_end(data):
    return data.get('fund_execution_period', {}).get('submission_end')

def get_funds(data):
    return data.get('funds')

def get_request_amount(data):
    return data.get('request_amount')

def get_official_info(data):
    return data.get('info_extra', {})

def get_eligible_recipients(data):
    return data.get('applicants', [])

def get_covered_expenses(data):
    return data.get('expenses', [])

def get_additional_info(data):
    return {
        'term': data.get('term'),
        'help_type': data.get('help_type'),
        'extra_info': data.get('info_extra')
    }

FUND_DETAILS_MAPPING = {
    'fund_slug': 'slug',
    'title': 'formatted_title',
    'purpose': 'goal_extra',
    'submission_period_opening': get_submission_start,
    'submission_period_closing': get_submission_end,
    'funds': get_funds,
    'scope': 'scope',
    'max_aid': get_request_amount,
    'official_info': get_official_info,
    'eligible_recipients': get_eligible_recipients,
    'covered_expenses': get_covered_expenses,
    'additional_info': get_additional_info
}

# Contador global de llamadas a la API
api_call_counter = {
    'funds': 0,
    'fund_details': 0,
    'total': 0
}

def decimal_default(obj):
    """
    Función auxiliar para serializar objetos Decimal y otros tipos especiales
    """
    try:
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        elif isinstance(obj, (date, time)):
            return str(obj)
        
        # Log para tipos no manejados explícitamente
        logger.debug(f"Convirtiendo tipo no manejado a string: {type(obj)}", 
                    extra={'operation': 'serialize', 'entity': 'json', 'status': 'warning'})
        return str(obj)
    except Exception as e:
        logger.error(f"Error serializando objeto de tipo {type(obj)}: {str(e)}", 
                    extra={'operation': 'serialize', 'entity': 'json', 'status': 'error'})
        return str(obj)

def setup_enhanced_logging():
    """
    Configura logging avanzado con rotación y monitoreo detallado
    """
    log_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] - '
        'Operation: %(operation)s - '
        'Entity: %(entity)s - '
        'Status: %(status)s - '
        'Details: %(message)s'
    )

    # Log file con rotación
    file_handler = RotatingFileHandler(
        'etl_fandit.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_formatter)

    # Console handler para debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Debug file handler para información detallada
    debug_handler = RotatingFileHandler(
        'etl_fandit_debug.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=3
    )
    debug_handler.setFormatter(log_formatter)
    debug_handler.setLevel(logging.DEBUG)

    # Configurar logger
    logger = logging.getLogger('etl_fandit')
    logger.setLevel(logging.DEBUG)  
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(debug_handler)

    return logger

# Configuración global
load_dotenv()
logger = setup_enhanced_logging()

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

async def validate_api_response(response: Dict[str, Any]) -> bool:
    """
    Valida la estructura y contenido de las respuestas de la API
    """
    try:
        if not response or 'results' not in response:
            logger.error("API no devuelve estructura esperada", 
                        extra={'operation': 'validate', 'entity': 'api', 'status': 'error'})
            return False
            
        # Log de la estructura completa de respuesta para debugging
        logger.debug(f"Estructura de respuesta API: {json.dumps(response, indent=2, default=decimal_default)}", 
                    extra={'operation': 'validate', 'entity': 'api', 'status': 'debug'})
            
        # Validar estructura de cada registro
        for fund in response['results'][:1]:  # Analizar primer registro
            logger.info("Validando estructura de registro", 
                       extra={'operation': 'validate', 'entity': 'fund', 'status': 'processing'})
            
            # Validar campos requeridos actualizados
            required_fields = ['formatted_title', 'status_text', 'total_amount', 'slug']
            missing_fields = [f for f in required_fields if f not in fund]
            if missing_fields:
                logger.error(f"Campos requeridos faltantes: {missing_fields}", 
                           extra={'operation': 'validate', 'entity': 'fund', 'status': 'error'})
                logger.debug(f"Registro con campos faltantes: {json.dumps(fund, indent=2, default=decimal_default)}", 
                           extra={'operation': 'validate', 'entity': 'fund', 'status': 'debug'})
            
            # Validar arrays JSON
            json_fields = ['provinces', 'communities', 'applicants', 'action_items', 
                         'origins', 'activities', 'region_types', 'types']
            for field in json_fields:
                if field in fund and not isinstance(fund[field], list):
                    logger.error(f"Campo {field} no es un array", 
                               extra={'operation': 'validate', 'entity': 'fund', 'status': 'error'})
                    logger.debug(f"Valor de {field}: {fund.get(field)}", 
                               extra={'operation': 'validate', 'entity': 'fund', 'status': 'debug'})
                    
            # Validar fechas
            date_fields = ['publication_date', 'end_date', 'final_period_start_date', 
                         'final_period_end_date']
            for field in date_fields:
                if field in fund and fund[field]:
                    try:
                        datetime.strptime(fund[field], '%Y-%m-%d')
                    except:
                        logger.error(f"Campo {field} no tiene formato de fecha válido", 
                                   extra={'operation': 'validate', 'entity': 'fund', 'status': 'error'})
                        logger.debug(f"Valor de {field}: {fund.get(field)}", 
                                   extra={'operation': 'validate', 'entity': 'fund', 'status': 'debug'})

        return True

    except Exception as e:
        logger.error(f"Error en validación: {str(e)}", 
                    extra={'operation': 'validate', 'entity': 'api', 'status': 'error'})
        return False

async def get_all_funds() -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene todas las subvenciones disponibles de la API incluyendo paginación
    """
    try:
        global api_call_counter
        all_results = []
        page = 1
        has_more = True
        
        request_data = {
            "is_open": True,  # Solo subvenciones abiertas
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
        
        logger.info("Iniciando obtención de subvenciones", 
                   extra={'operation': 'api_request', 'entity': 'funds', 'status': 'start'})

        while has_more:
            api_call_counter['funds'] += 1
            api_call_counter['total'] += 1
            logger.info(f"Llamada API #{api_call_counter['funds']} a /funds/", 
                       extra={'operation': 'api_call', 'entity': 'funds', 'status': 'info'})
            
            response = await api.obtener_lista_subvenciones(page=page, request_data=request_data)
            
            if not response or 'results' not in response:
                logger.error(f"Error en respuesta de API página {page}", 
                           extra={'operation': 'api_error', 'entity': 'funds', 'status': 'error'})
                break

            # Log de respuesta completa para debugging
            logger.debug(f"Respuesta API página {page}: {json.dumps(response, indent=2, default=decimal_default)}", 
                        extra={'operation': 'api_response', 'entity': 'funds', 'status': 'debug'})

            if page == 1:  # Solo en la primera página
                logger.info(f"Total de subvenciones abiertas encontradas: {response.get('count', 0)}", 
                          extra={'operation': 'api_request', 'entity': 'funds', 'status': 'info'})

            # Validar respuesta
            if not await validate_api_response(response):
                logger.error(f"Validación falló para página {page}", 
                           extra={'operation': 'validate', 'entity': 'funds', 'status': 'error'})
                break

            results = response.get('results', [])
            all_results.extend(results)
            
            # Verificar si hay más páginas
            next_page = response.get('next')
            has_more = next_page is not None
            
            if has_more:
                page += 1
                logger.info(f"Procesando página {page} de {response.get('count', 0)} registros totales", 
                          extra={'operation': 'pagination', 'entity': 'funds', 'status': 'info'})
            
            logger.info(f"Página {page} procesada. Registros acumulados: {len(all_results)}", 
                       extra={'operation': 'pagination', 'entity': 'funds', 'status': 'success'})

        logger.info(f"Total de registros obtenidos: {len(all_results)}", 
                   extra={'operation': 'complete', 'entity': 'funds', 'status': 'success'})
        
        return {'results': all_results}

    except Exception as e:
        logger.error(f"Error obteniendo subvenciones: {str(e)}", 
                    extra={'operation': 'api_error', 'entity': 'funds', 'status': 'error'})
        raise

def update_fund(cursor: mysql.connector.cursor.MySQLCursor, fund_data: Dict[str, Any]) -> bool:
    """
    Actualiza o inserta un registro de fund usando el mapeo definido
    """
    slug = fund_data.get('slug', '')
    
    try:
        # Obtener registro actual si existe
        check_sql = "SELECT * FROM funds WHERE slug = %s"
        cursor.execute(check_sql, (slug,))
        columns = [desc[0] for desc in cursor.description]
        result = cursor.fetchone()
        
        # Generar new_data usando el mapeo
        new_data = {}
        for db_field, mapping in FUNDS_MAPPING.items():
            if callable(mapping):
                # Si es una función lambda
                new_data[db_field] = mapping(fund_data)
            else:
                # Si es un mapeo directo
                new_data[db_field] = fund_data.get(mapping)

            # Convertir listas/diccionarios a JSON
            if isinstance(new_data[db_field], (list, dict)):
                new_data[db_field] = json.dumps(new_data[db_field])
        
        if result:
            # Comparar y actualizar campos modificados
            current_data = dict(zip(columns, result))
            
            # Log para debugging de datos actuales y nuevos
            logger.debug(f"Datos actuales: {json.dumps(current_data, indent=2, default=decimal_default)}", 
                        extra={'operation': 'check', 'entity': 'funds', 'status': 'debug'})
            logger.debug(f"Datos nuevos: {json.dumps(new_data, indent=2, default=decimal_default)}", 
                        extra={'operation': 'check', 'entity': 'funds', 'status': 'debug'})
            
            # Detectar cambios
            changes = []
            update_fields = []
            update_values = []
            
            for field, new_value in new_data.items():
                current_value = current_data.get(field)
                
                # Convertir bytes a string para comparación
                if isinstance(current_value, bytes):
                    current_value = current_value.decode('utf-8')
                
                # Convertir Decimal a float para comparación
                if isinstance(current_value, Decimal):
                    current_value = float(current_value)
                
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
                            'entity': f'funds/{slug}',
                            'status': 'success'
                        }
                    )
                
                return True
            
            logger.info(
                "No se detectaron cambios",
                extra={'operation': 'check', 'entity': f'funds/{slug}', 'status': 'unchanged'}
            )
            return False
            
        else:
            # Insertar nuevo registro
            columns = list(FUNDS_MAPPING.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            
            insert_sql = f"""
            INSERT INTO funds ({', '.join(columns)})
            VALUES ({placeholders})
            """
            
            values = tuple(new_data[col] for col in columns)
            cursor.execute(insert_sql, values)
            
            logger.info(
                f"Nueva subvención creada",
                extra={
                    'operation': 'insert',
                    'entity': f'funds/{slug}',
                    'status': 'success'
                }
            )
            return True
            
    except Exception as e:
        logger.error(
            f"Error procesando subvención: {str(e)}",
            extra={
                'operation': 'error',
                'entity': f'funds/{slug}',
                'status': 'error'
            }
        )
        raise

async def update_fund_details(cursor: mysql.connector.cursor.MySQLCursor, fund_slug: str) -> bool:
    """
    Actualiza o inserta detalles de una subvención usando el mapeo definido
    """
    try:
        global api_call_counter
        api_call_counter['fund_details'] += 1
        api_call_counter['total'] += 1
        
        logger.info(f"Llamada API #{api_call_counter['fund_details']} a /fund-details/", 
                   extra={'operation': 'api_call', 'entity': 'fund_details', 'status': 'info'})
        
        details = await api.obtener_detalle_subvencion(fund_slug)
        if not details:
            logger.error(f"No se obtuvieron detalles para {fund_slug}", 
                        extra={'operation': 'api_request', 'entity': 'fund_details', 'status': 'error'})
            return False

        # Log de detalles para debugging
        logger.debug(f"Detalles obtenidos para {fund_slug}: {json.dumps(details, indent=2, default=decimal_default)}", 
                    extra={'operation': 'api_response', 'entity': 'fund_details', 'status': 'debug'})

        # Generar new_data usando el mapeo
        new_data = {}
        for db_field, mapping in FUND_DETAILS_MAPPING.items():
            if callable(mapping):
                # Si es una función lambda
                new_data[db_field] = mapping(details)
            else:
                # Si es un mapeo directo
                new_data[db_field] = details.get(mapping)

            # Convertir listas/diccionarios a JSON
            if isinstance(new_data[db_field], (list, dict)):
                new_data[db_field] = json.dumps(new_data[db_field])

        # Verificar si existe
        check_sql = "SELECT id FROM fund_details WHERE fund_slug = %s"
        cursor.execute(check_sql, (fund_slug,))
        exists = cursor.fetchone()
        
        if exists:
            # Update
            update_fields = [f"{field} = %s" for field in new_data.keys()]
            update_sql = f"""
            UPDATE fund_details SET
                {', '.join(update_fields)},
                updated_at = NOW()
            WHERE fund_slug = %s
            """
            values = list(new_data.values()) + [fund_slug]
            cursor.execute(update_sql, values)
            
            logger.info(f"Detalles actualizados para {fund_slug}",
                       extra={'operation': 'update', 'entity': 'fund_details', 'status': 'success'})
            return True
        else:
            # Insert
            columns = list(new_data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"""
            INSERT INTO fund_details (
                {', '.join(columns)}
            ) VALUES ({placeholders})
            """
            values = list(new_data.values())
            
            cursor.execute(insert_sql, values)
            
            logger.info(f"Nuevos detalles creados para {fund_slug}",
                       extra={'operation': 'insert', 'entity': 'fund_details', 'status': 'success'})
            return True

    except Exception as e:
        logger.error(f"Error actualizando fund_details para {fund_slug}: {str(e)}",
                    extra={'operation': 'error', 'entity': 'fund_details', 'status': 'error'})
        return False

async def main():
    """
    Proceso ETL principal con validaciones
    """
    try:
        logger.info("Iniciando proceso ETL", 
                   extra={'operation': 'start', 'entity': 'etl', 'status': 'init'})
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        try:
            # Obtener y procesar datos
            funds_data = await get_all_funds()
            
            if funds_data and 'results' in funds_data:
                updates = {'funds': 0, 'fund_details': 0}
                total_registros = len(funds_data['results'])
                
                logger.info(f"Procesando {total_registros} registros", 
                          extra={'operation': 'process', 'entity': 'etl', 'status': 'processing'})
                
                for i, fund in enumerate(funds_data['results'], 1):
                    logger.info(f"Procesando registro {i} de {total_registros}", 
                              extra={'operation': 'process', 'entity': 'etl', 'status': 'processing'})
                    
                    # Actualizar funds
                    if update_fund(cursor, fund):
                        updates['funds'] += 1
                        
                    # Actualizar fund_details
                    if await update_fund_details(cursor, fund['slug']):
                        updates['fund_details'] += 1
                
                conn.commit()
                
                # Log del resumen de llamadas a la API
                logger.info(
                    f"Total llamadas API: {api_call_counter['total']} "
                    f"(funds: {api_call_counter['funds']}, "
                    f"fund_details: {api_call_counter['fund_details']})",
                    extra={
                        'operation': 'summary',
                        'entity': 'api',
                        'status': 'info'
                    }
                )
                
                logger.info(
                    f"Proceso completado. Actualizaciones: Funds={updates['funds']}, Details={updates['fund_details']}",
                    extra={
                        'operation': 'complete',
                        'entity': 'etl',
                        'status': 'success'
                    }
                )
            else:
                logger.error(
                    "No se obtuvieron datos de la API",
                    extra={
                        'operation': 'complete',
                        'entity': 'etl',
                        'status': 'error'
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
                'entity': 'etl',
                'status': 'failed'
            }
        )
        raise

if __name__ == "__main__":
    asyncio.run(main())