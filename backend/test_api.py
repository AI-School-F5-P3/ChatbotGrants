import asyncio
import json
from clase_apifandit import FanditAPI
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api():
    # Inicializar API
    api = FanditAPI(
        token=os.getenv("FANDIT_TOKEN"),
        expert_token=os.getenv("FANDIT_EXPERT_TOKEN")
    )

    # Test 1: Obtener lista de subvenciones
    print("\nTest 1: Obtener lista de subvenciones")
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
    
    funds = await api.obtener_lista_subvenciones(page=1, request_data=request_data)
    print(json.dumps(funds, indent=2))

    if funds and 'results' in funds:
        # Test 2: Obtener detalles de la primera subvención
        print("\nTest 2: Obtener detalles de la primera subvención")
        first_fund = funds['results'][0]
        if 'slug' in first_fund:
            details = await api.obtener_detalle_subvencion(first_fund['slug'])
            print(json.dumps(details, indent=2))

if __name__ == "__main__":
    asyncio.run(test_api())