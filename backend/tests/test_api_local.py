import asyncio
import aiohttp
import pandas as pd
import os
from datetime import datetime
import logging
import json

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,  # Cambiado a DEBUG para más detalles
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('convocatorias_debug.log'),  # Log a archivo
        logging.StreamHandler()  # Log a consola
    ]
)
logger = logging.getLogger(__name__)

# Configuración de parámetros
START_PAGE = 10675  # Comenzar desde la página 10675
END_PAGE = 10800    # Aumentar el rango de páginas
PAGE_SIZE = 50
OUTPUT_DIR = 'output'

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_data(session, url, params=None, timeout=30):
    """Función para realizar solicitudes HTTP con manejo de errores"""
    try:
        async with session.get(url, params=params, timeout=timeout) as response:
            logger.debug(f"URL: {url}, Params: {params}, Status: {response.status}")
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Error en la solicitud: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error en fetch_data: {str(e)}")
        return None

async def process_convocatorias():
    """Procesar convocatorias de múltiples páginas de forma asíncrona"""
    async with aiohttp.ClientSession() as session:
        # Listas para almacenar datos
        resumen_convocatorias = []
        detalle_convocatorias = []
        total_convocatorias_filtradas = 0

        # Procesar páginas de forma concurrente
        for page in range(START_PAGE, END_PAGE + 1):
            # Parámetros de búsqueda
            search_params = {
                "vpd": "GE",
                "pageSize": PAGE_SIZE,
                "page": page,
                "direccion": "desc"
            }
            
            # URL base
            base_url = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias/busqueda"
            
            # Obtener lista de convocatorias
            response = await fetch_data(session, base_url, search_params)
            
            if not response or 'content' not in response:
                logger.warning(f"No se encontraron datos en la página {page}")
                continue
            
            convocatorias = response['content']
            logger.info(f"Procesando página {page}: {len(convocatorias)} convocatorias")

            # Procesar cada convocatoria
            for conv in convocatorias:
                try:
                    # Obtener detalle de la convocatoria
                    detail_params = {
                        "vpd": "GE",
                        "numConv": conv['numeroConvocatoria']
                    }
                    detail_url = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias"
                    detail = await fetch_data(session, detail_url, detail_params)
                    
                    if not detail:
                        continue

                    # Verificar si tiene fecha de recepción en 2024 o 2025
                    fecha_recepcion = detail.get('fechaRecepcion')
                    if not fecha_recepcion:
                        logger.debug(f"Convocatoria {conv['numeroConvocatoria']} sin fecha de recepción")
                        continue

                    logger.debug(f"Fecha recepción: {fecha_recepcion}")

                    # Modificado para filtrar 2024 y 2025
                    if fecha_recepcion.startswith(('2024', '2025')):
                        total_convocatorias_filtradas += 1
                        
                        # Agregar información de resumen
                        resumen_convocatorias.append({
                            'numero_convocatoria': conv.get('numeroConvocatoria'),
                            'titulo': conv.get('titulo', ''),
                            'fecha_recepcion': fecha_recepcion,
                            'page': page
                        })

                        # Combinamos toda la información disponible
                        detalle_completo = {**conv, **detail}
                        detalle_convocatorias.append(detalle_completo)

                except Exception as e:
                    logger.error(f"Error procesando convocatoria {conv.get('numeroConvocatoria')}: {str(e)}")

            # Guardar resultados parciales cada 10 páginas
            if page % 10 == 0:
                guardar_resultados_parciales(resumen_convocatorias, detalle_convocatorias)

        # Resumen final
        logger.info(f"Total de convocatorias con fecha de recepción 2024/2025: {total_convocatorias_filtradas}")

        # Guardar resultados finales
        guardar_resultados_parciales(resumen_convocatorias, detalle_convocatorias, final=True)

def guardar_resultados_parciales(resumen, detalle, final=False):
    """Guardar resultados en archivos CSV"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sufijo = 'final' if final else 'parcial'

        # Logging adicional
        logger.info(f"Guardando resultados - Resumen: {len(resumen)} registros, Detalle: {len(detalle)} registros")

        # Asegurar que hay datos
        if resumen:
            df_resumen = pd.DataFrame(resumen)
            resumen_path = os.path.join(OUTPUT_DIR, f'resumen_convocatorias_{timestamp}_{sufijo}.csv')
            df_resumen.to_csv(resumen_path, index=False, encoding='utf-8')
            logger.info(f"Guardado resumen: {resumen_path}")

        if detalle:
            df_detalle = pd.DataFrame(detalle)
            detalle_path = os.path.join(OUTPUT_DIR, f'detalle_convocatorias_{timestamp}_{sufijo}.csv')
            df_detalle.to_csv(detalle_path, index=False, encoding='utf-8')
            logger.info(f"Guardado detalle: {detalle_path}")

    except Exception as e:
        logger.error(f"Error guardando archivos: {str(e)}")

def main():
    # Medir tiempo de ejecución
    start_time = datetime.now()
    logger.info("Iniciando proceso de descarga de convocatorias...")

    # Ejecutar proceso asíncrono
    asyncio.run(process_convocatorias())

    # Calcular tiempo total
    end_time = datetime.now()
    logger.info(f"Proceso completado. Tiempo total: {end_time - start_time}")

if __name__ == "__main__":
    main()