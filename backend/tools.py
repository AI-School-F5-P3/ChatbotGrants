# tools.py
import os
import mysql.connector
from dotenv import load_dotenv
import json

class GrantsDatabase:
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()
        
        # Configuración de conexión
        self.connection_config = {
            'host': os.getenv('AURORA_CLUSTER_ENDPOINT'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': 'fandit_db'
        }
    
    def _get_connection(self):
        """Establecer conexión a la base de datos"""
        return mysql.connector.connect(**self.connection_config)
    
    def load_grants(self, limit=10):
        """Cargar subvenciones desde la base de datos"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT * FROM funds 
                WHERE is_open = TRUE 
                ORDER BY total_amount DESC 
                LIMIT %s
                """
                cursor.execute(query, (limit,))
                return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al cargar subvenciones: {err}")
            return []

    def find_best_grant(self, user_info=None):
        """Encontrar las mejores subvenciones basadas en criterios"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Consulta base que puede ser refinada según user_info
                query = """
                SELECT * FROM funds 
                WHERE is_open = TRUE 
                ORDER BY total_amount DESC 
                LIMIT 3
                """
                
                # Si se proporcionan más detalles de usuario, se puede refinar la consulta
                if user_info:
                    # Ejemplo de posible refinamiento
                    conditions = []
                    params = []
                    
                    if 'applicant_type' in user_info:
                        conditions.append("JSON_CONTAINS(applicants, %s)")
                        params.append(json.dumps(user_info['applicant_type']))
                    
                    if conditions:
                        query = f"""
                        SELECT * FROM funds 
                        WHERE is_open = TRUE 
                        AND {' AND '.join(conditions)}
                        ORDER BY total_amount DESC 
                        LIMIT 3
                        """
                
                cursor.execute(query, params if conditions else None)
                return cursor.fetchall()
        
        except mysql.connector.Error as err:
            print(f"Error al encontrar mejores subvenciones: {err}")
            return []

    def get_grant_detail(self, bdns):
        """Obtener detalles de una subvención específica por BDNS"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Primero buscar en funds
                query_funds = """
                SELECT * FROM funds 
                WHERE bdns = %s
                """
                cursor.execute(query_funds, (bdns,))
                fund = cursor.fetchone()
                
                # Luego buscar en fund_details
                query_details = """
                SELECT * FROM fund_details 
                WHERE JSON_EXTRACT(official_info, '$.bdns') = %s
                """
                cursor.execute(query_details, (bdns,))
                details = cursor.fetchone()
                
                # Combinar resultados
                if fund and details:
                    combined_result = {**fund, **details}
                    return combined_result
                
                return None
        
        except mysql.connector.Error as err:
            print(f"Error al obtener detalles de subvención: {err}")
            return None

def main():
    # Probar las funciones
    grants_db = GrantsDatabase()
    
    # Probar carga de subvenciones
    print("Subvenciones disponibles:")
    grants = grants_db.load_grants(limit=3)
    for grant in grants:
        print(json.dumps(grant, indent=2))
    
    # Probar búsqueda de mejores subvenciones
    print("\nMejores subvenciones:")
    best_grants = grants_db.find_best_grant()
    for grant in best_grants:
        print(json.dumps(grant, indent=2))
    
    # Probar obtener detalle de subvención
    if grants:
        bdns = grants[0].get('bdns')
        print(f"\nDetalle de subvención con BDNS {bdns}:")
        detail = grants_db.get_grant_detail(bdns)
        print(json.dumps(detail, indent=2))

if __name__ == "__main__":
    main()