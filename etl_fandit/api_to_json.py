import asyncio
import json
import os
from datetime import datetime

import aiohttp
from dotenv import load_dotenv

#Script que descarga json con subvenciones de la API de Fandit y las guarda en un archivo JSON.
#Última version actualizada al 2025-02-20

from clase_apifandit import FanditAPI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

async def descargar_subvenciones(api, paginas_a_descargar=None):
    """
    Descarga subvenciones de la API de Fandit y las guarda en un archivo JSON.
    
    :param api: Instancia de FanditAPI
    :param paginas_a_descargar: Número de páginas a descargar (None para todas)
    :return: Lista completa de subvenciones
    """
    todas_subvenciones = []
    
    filtros_base = {
        "is_open": True,
        "start_date": None,
        "end_date": None,
        "final_period_start_date": None,
        "final_period_end_date": None,
        "provinces": [],
        "applicants": [],
        "communities": [],
        "action_items": [],
        "origins": [],
        "activities": [],
        "region_types": [],
        "types": []
    }
    
    # Obtener primera página para ver el total
    primera_respuesta = await api.obtener_lista_subvenciones(page=1, request_data=filtros_base)
    if not primera_respuesta:
        print("No se pudo obtener la primera página")
        return []
        
    total_registros = primera_respuesta.get('count', 0)
    registros_por_pagina = len(primera_respuesta.get('results', []))
    total_paginas = -(-total_registros // registros_por_pagina)  # Redondeo hacia arriba
    
    print(f"Total de registros disponibles: {total_registros}")
    print(f"Registros por página: {registros_por_pagina}")
    print(f"Total de páginas: {total_paginas}")
    
    # Añadir resultados de la primera página
    todas_subvenciones.extend(primera_respuesta.get('results', []))
    
    # Descargar el resto de páginas
    max_paginas = paginas_a_descargar if paginas_a_descargar else total_paginas
    for pagina in range(2, max_paginas + 1):
        print(f"Descargando página {pagina} de {max_paginas}...")
        
        respuesta = await api.obtener_lista_subvenciones(page=pagina, request_data=filtros_base)
        if respuesta and 'results' in respuesta:
            subvenciones_pagina = respuesta['results']
            todas_subvenciones.extend(subvenciones_pagina)
            
            if not respuesta.get('next'):
                print("No hay más páginas disponibles")
                break
        else:
            print(f"No se encontraron resultados en la página {pagina}")
            break
            
        # Pequeña pausa para no sobrecargar la API
        await asyncio.sleep(0.5)
    
    print(f"Total de subvenciones descargadas: {len(todas_subvenciones)}")
    return todas_subvenciones


async def obtener_detalles_subvenciones(api, subvenciones):
    """
    Obtiene los detalles completos de cada subvención.
    
    :param api: Instancia de FanditAPI
    :param subvenciones: Lista de subvenciones base
    :return: Lista de subvenciones con detalles completos
    """
    subvenciones_con_detalles = []
    
    for subvencion in subvenciones:
        try:
            detalle = await api.obtener_detalle_subvencion(subvencion['slug'])
            # Combinar los datos base con los detalles
            subvencion_completa = {**subvencion, **detalle}
            subvenciones_con_detalles.append(subvencion_completa)
            print(f"Detalle obtenido para: {subvencion['slug']}")
        except Exception as e:
            print(f"Error al obtener detalle de {subvencion['slug']}: {e}")
    
    return subvenciones_con_detalles

def guardar_json(datos, nombre_archivo=None):
    """
    Guarda los datos en un archivo JSON.
    
    :param datos: Datos a guardar
    :param nombre_archivo: Nombre del archivo (si no se especifica, se usa la fecha actual)
    """
    if not nombre_archivo:
        # Crear nombre de archivo con fecha y hora actual
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"subvenciones_{fecha_actual}.json"
    
    # Crear directorio de salida si no existe
    os.makedirs('output', exist_ok=True)
    ruta_completa = os.path.join('output', nombre_archivo)
    
    with open(ruta_completa, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    
    print(f"Datos guardados en {ruta_completa}")

async def main():
    # Obtener tokens y credenciales del archivo .env
    token = os.getenv('FANDIT_TOKEN')
    expert_token = os.getenv('FANDIT_EXPERT_TOKEN')
    email = os.getenv('FANDIT_EMAIL')  # Opcional
    password = os.getenv('FANDIT_PASSWORD')  # Opcional
    
    # Verificar que los tokens estén presentes
    if not token or not expert_token:
        print("Error: Tokens no encontrados en el archivo .env")
        return
    
    # Inicializar la API con los tokens
    api = FanditAPI(
        token=token, 
        expert_token=expert_token, 
        email=email,  
        password=password  
    )
    
    try:
        # Intentar renovar el token primero
        if email and password:
            await api.refrescar_token()
        
        # 1. Descargar lista de subvenciones (todas las páginas)
        subvenciones = await descargar_subvenciones(api, paginas_a_descargar=None)
        print(f"Total de subvenciones base descargadas: {len(subvenciones)}")
        
        # Verificar si se descargaron subvenciones
        if not subvenciones:
            print("No se descargaron subvenciones. Verificar credenciales y configuración.")
            return
        
        # 2. Obtener detalles de cada subvención
        subvenciones_completas = await obtener_detalles_subvenciones(api, subvenciones)
        
        # 3. Guardar en JSON
        guardar_json(subvenciones_completas)
        
    except Exception as e:
        print(f"Error en el proceso: {e}")
        # Imprimir información adicional de depuración
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())