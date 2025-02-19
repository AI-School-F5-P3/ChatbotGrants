import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from clase_apifandit import FanditAPI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

async def test_funds_endpoint_comprehensive():
    """
    Prueba exhaustiva del endpoint /funds/ de Fandit API
    Objetivo: Validar todos los campos documentados y entender discrepancias
    """
    # Obtener tokens desde .env
    token = os.getenv('FANDIT_TOKEN')
    expert_token = os.getenv('FANDIT_EXPERT_TOKEN')
    
    # Verificar que los tokens estén presentes
    if not token or not expert_token:
        print("Error: Tokens no encontrados en el archivo .env")
        return
    
    # Inicializar la API con los tokens
    api = FanditAPI(
        token=token, 
        expert_token=expert_token
    )
    
    try:
        # Filtros comprehensivos según documentación
        filtros_base = {
            # Campos booleanos y de texto
            "is_open": True,
            "search_by_text": None,
            
            # Campos de presupuesto
            "max_budget": None,
            "max_total_amount": None,
            "min_total_amount": None,
            
            # Campos de identificación
            "bdns": None,
            "office": "",
            
            # Campos de fechas
            "start_date": "2024-01-01",
            "end_date": "2025-12-31",
            "final_period_start_date": "2024-01-01",
            "final_period_end_date": "2025-12-31",
            
            # Campos de búsqueda específica
            "search_tab": None,
            
            # Arrays de filtrado
            "provinces": [],
            "applicants": [],
            "communities": [],
            "action_items": [],
            "origins": [],
            "activities": [],
            "region_types": [],
            "types": []
        }
        
        # Realizar la solicitud a la API
        print("=== Realizando solicitud al endpoint /funds/ ===")
        print("Filtros comprehensivos enviados:")
        print(json.dumps(filtros_base, indent=2))
        
        # Descargar primera página de subvenciones
        respuesta = await api.obtener_lista_subvenciones(page=1, request_data=filtros_base)
        
        # Debug: Imprimir tipo y contenido crudo de la respuesta
        print("\n=== Depuración de Respuesta Cruda ===")
        print("Tipo de respuesta:", type(respuesta))
        print("Claves de primer nivel:", list(respuesta.keys()) if isinstance(respuesta, dict) else "No es un diccionario")
        
        # Análisis detallado de estructura de respuesta
        if not isinstance(respuesta, dict):
            print("ALERTA: La respuesta NO es un diccionario. Tipo recibido:", type(respuesta))
            # Intentar convertir a diccionario si es posible
            try:
                respuesta = dict(respuesta)
            except Exception as e:
                print("No se pudo convertir la respuesta a diccionario:", e)
                return
        
        # Comparación de campos documentados vs recibidos
        campos_documentados = [
            "is_open", "search_by_text", "max_budget", "max_total_amount", 
            "min_total_amount", "bdns", "office", "start_date", "end_date", 
            "final_period_end_date", "final_period_start_date", "search_tab",
            "provinces", "applicants", "communities", "action_items", 
            "origins", "activities", "region_types", "types"
        ]
        
        # Análisis de los resultados
        if 'results' not in respuesta:
            print("ALERTA: No se encontró la clave 'results' en la respuesta")
            print("Claves disponibles:", list(respuesta.keys()))
            return
        
        print(f"\nNúmero de subvenciones: {len(respuesta['results'])}")
        
        # Análisis detallado del primer resultado
        if respuesta['results']:
            primer_resultado = respuesta['results'][0]
            
            print("\n=== Análisis Comparativo de Campos ===")
            campos_resultado = list(primer_resultado.keys())
            
            # Campos en la documentación no presentes en el resultado
            campos_faltantes = [
                campo for campo in campos_documentados 
                if campo not in campos_resultado
            ]
            
            # Campos en el resultado no documentados
            campos_adicionales = [
                campo for campo in campos_resultado 
                if campo not in campos_documentados
            ]
            
            print("\nCampos documentados NO encontrados:")
            for campo in campos_faltantes:
                print(f"- {campo}")
            
            print("\nCampos ADICIONALES encontrados:")
            for campo in campos_adicionales:
                print(f"- {campo}")
            
            print("\n=== Contenido Detallado ===")
            for campo in campos_resultado:
                valor = primer_resultado[campo]
                print(f"\n{campo}:")
                try:
                    valor_str = json.dumps(valor, ensure_ascii=False)
                    print(valor_str[:500] + ('' if len(valor_str) <= 500 else '...'))
                except Exception as e:
                    print(f"Error al serializar {campo}: {e}")
        
        # Guardar respuesta completa para análisis posterior
        os.makedirs('output', exist_ok=True)
        ruta_salida = os.path.join('output', f'respuesta_funds_endpoint_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(respuesta, f, ensure_ascii=False, indent=2)
        print(f"\nRespuesta completa guardada en {ruta_salida}")
        
    except Exception as e:
        print(f"Error en el proceso: {e}")
        import traceback
        traceback.print_exc()

# Ejecutar el test
if __name__ == "__main__":
    asyncio.run(test_funds_endpoint_comprehensive())