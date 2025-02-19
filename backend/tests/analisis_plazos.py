import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_data(session, url, params):
    async with session.get(url, params=params) as response:
        if response.status == 200:
            return await response.json()
    return None

async def analyze_plazos():
    """Analiza los patrones de plazos en convocatorias abiertas"""
    base_url = "https://www.infosubvenciones.es/bdnstrans/api"
    
    async with aiohttp.ClientSession() as session:
        # Obtener una muestra de convocatorias abiertas
        params = {
            "vpd": "GE",
            "pageSize": 50,
            "direccion": "desc"
        }
        
        response = await fetch_data(session, f"{base_url}/convocatorias/busqueda", params)
        if not response or 'content' not in response:
            logger.error("No se pudieron obtener convocatorias")
            return
        
        plazos_data = []
        
        for conv in response['content']:
            detail_params = {
                "vpd": "GE",
                "numConv": conv['numeroConvocatoria']
            }
            
            detail = await fetch_data(session, f"{base_url}/convocatorias", detail_params)
            if detail and detail.get('abierto', False):
                try:
                    fecha_recepcion = datetime.strptime(detail['fechaRecepcion'], '%Y-%m-%d')
                    fecha_fin = datetime.strptime(detail.get('fechaFinSolicitud', ''), '%Y-%m-%d') if detail.get('fechaFinSolicitud') else None
                    
                    plazos_data.append({
                        'numero_convocatoria': conv['numeroConvocatoria'],
                        'fecha_recepcion': fecha_recepcion,
                        'fecha_fin': fecha_fin,
                        'dias_plazo': (fecha_fin - fecha_recepcion).days if fecha_fin else None
                    })
                except Exception as e:
                    logger.warning(f"Error procesando fechas para convocatoria {conv['numeroConvocatoria']}: {str(e)}")
        
        # Análisis de los plazos
        df = pd.DataFrame(plazos_data)
        
        print("\n=== ANÁLISIS DE PLAZOS EN CONVOCATORIAS ABIERTAS ===")
        print(f"\nTotal convocatorias analizadas: {len(df)}")
        
        if not df.empty:
            print("\nEstadísticas de días de plazo:")
            print(df['dias_plazo'].describe())
            
            print("\nConvocatoria más antigua aún abierta:")
            oldest = df.nsmallest(1, 'fecha_recepcion').iloc[0]
            print(f"Número: {oldest['numero_convocatoria']}")
            print(f"Fecha recepción: {oldest['fecha_recepcion']}")
            print(f"Fecha fin: {oldest['fecha_fin']}")
            print(f"Días de plazo: {oldest['dias_plazo']}")
            
            # Guardar resultados detallados
            df.to_csv('analisis_plazos.csv', index=False)
            print("\nResultados detallados guardados en 'analisis_plazos.csv'")

if __name__ == "__main__":
    asyncio.run(analyze_plazos())