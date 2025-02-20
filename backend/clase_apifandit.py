import aiohttp
import json
import asyncio

class FanditAPI:
    def __init__(self, token, expert_token, base_url="https://ayming.api.fandit.es/api/v2", email=None, password=None):
        """
        Inicializa la clase con los tokens necesarios y, opcionalmente, las credenciales para renovar el token (en este caso no es necesario 😉).
        """
        self.token = token
        self.expert_token = expert_token
        self.base_url = base_url
        self.email = email
        self.password = password

    def _headers(self, tipo="usuario"):
        """
        Devuelve los headers necesarios según el tipo de endpoint.
        """
        if tipo == "usuario":
            return {"Content-Type": "application/json", "Authorization": f"Token {self.token}"}
        elif tipo == "expert":
            return {"Content-Type": "application/json", "Authorization": f"ExpertToken {self.expert_token}"}
        else:
            return {"Content-Type": "application/json"}

    async def _request(self, metodo, endpoint, headers_tipo="usuario", params=None, data=None, json_data=None, intento=1):
        """
        Método interno asíncrono que realiza las peticiones HTTP, controlando errores y, en caso de 401, intenta refrescar el token.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._headers(tipo=headers_tipo)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(metodo, url, headers=headers, params=params, data=data, json=json_data) as response:
                    if response.status == 401 and intento <= 1:
                        print("Token expirado o inválido. Se intentará renovar el token...")
                        if self.email and self.password:
                            await self.refrescar_token()
                            return await self._request(metodo, endpoint, headers_tipo, params, data, json_data, intento + 1)
                        else:
                            response.raise_for_status()
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                print(f"Error en la petición a {url}: {e}")
                return None

    async def refrescar_token(self):
        """
        Renueva el token del usuario utilizando las credenciales (email y password) a través del endpoint /users/login/.
        Actualiza el atributo self.token con el nuevo token.
        """
        url_login = f"{self.base_url}/users/login/"
        payload = {"email": self.email, "password": self.password}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url_login, json=payload) as response:
                    response.raise_for_status()
                    datos = await response.json()
                    self.token = datos.get("token")
                    print("Token actualizado correctamente.")
                    return self.token
            except aiohttp.ClientError as e:
                print(f"Error al renovar token: {e}")
                return None

    async def obtener_lista_subvenciones(self, page=1, request_data=None):
        """
        Obtiene la lista de subvenciones.
        Endpoint: /funds/
        """
        if request_data is None:
            request_data = {}
        params = {"page": page, "requestData": json.dumps(request_data)}
        return await self._request("GET", "/funds/", headers_tipo="expert", params=params)

    async def obtener_lista_concesiones(self, page=1, request_data=None):
        """
        Obtiene la lista de concesiones de subvenciones.
        Endpoint: /funds/concessions/
        """
        if request_data is None:
            request_data = {}
        params = {"page": page, "requestData": json.dumps(request_data)}
        return await self._request("GET", "/funds/concessions/", headers_tipo="expert", params=params)

    async def obtener_lista_beneficiarios_concesiones(self, page=1, request_data=None):
        """
        Obtiene la lista de beneficiarios de concesiones.
        Endpoint: /funds/concessions/beneficiaries/
        """
        if request_data is None:
            request_data = {}
        params = {"page": page, "requestData": json.dumps(request_data)}
        return await self._request("GET", "/funds/concessions/beneficiaries/", headers_tipo="expert", params=params)

    async def obtener_detalle_subvencion(self, fund_slug):
        """
        Obtiene el detalle de una subvención a través de su slug.
        Endpoint: /fund-details/<fund_slug>/
        """
        endpoint = f"/fund-details/{fund_slug}/"
        return await self._request("GET", endpoint, headers_tipo="expert")


if __name__ == "__main__":

    ##########################################
    # NOTA: OS HE DEJADO LOS TOKENS EN EL S3 #
    ##########################################
    
    api = FanditAPI(
        token="",
        expert_token=""
    )

    # Prueba del endpoint /funds/ (Lista de Subvenciones)
    print("\n=== Prueba del endpoint /funds/ (Lista de Subvenciones) ===")
    filtros_subvenciones = {
        "is_open": True,
        "start_date": None, "2025-01-01"
        "end_date": None, "2025-03-30"
        "final_period_start_date": None, "2025-01-01"
        "final_period_end_date": None,"2025-04-30"
        "provinces": [],
        "applicants": [],
        "communities": [],
        "action_items": [],
        "origins": [],
        "activities": [],
        "region_types": [],
        "types": []
    }
    subvenciones = asyncio.run(api.obtener_lista_subvenciones(page=1, request_data=filtros_subvenciones))
    print("Lista de subvenciones:", subvenciones)

    # Prueba del endpoint /funds/concessions/ (Lista de Concesiones)
    print("\n=== Prueba del endpoint /funds/concessions/ (Lista de Concesiones) ===")
    filtros_concesiones = {
        "is_open": True,
        "start_date": "2025-01-01",
        "end_date": "2025-04-30",
        "final_period_start_date": "2025-01-01",
        "final_period_end_date": "2025-04-30",
        "provinces": [],
        "applicants": [],
        "communities": [],
        "action_items": [],
        "origins": [],
        "activities": [],
        "region_types": [],
        "types": []
    }
    concesiones = asyncio.run(api.obtener_lista_concesiones(page=1, request_data=filtros_concesiones))
    print("Lista de concesiones:", concesiones)

    # Prueba del endpoint /funds/concessions/beneficiaries/ (Beneficiarios de Concesiones)
    print("\n=== Prueba del endpoint /funds/concessions/beneficiaries/ (Beneficiarios de Concesiones) ===")
    filtros_beneficiarios = {
        "nif": "",
        "fund_slug": "ayudas-para-startups-tecnologicas-innovadoras-del-programa-neotec-ano-2024"
    }
    beneficiarios = asyncio.run(api.obtener_lista_beneficiarios_concesiones(page=1, request_data=filtros_beneficiarios))
    print("Beneficiarios de concesiones:", beneficiarios)

    # Prueba del endpoint /fund-details/<fund-slug>/ (Detalle de Subvención)
    print("\n=== Prueba del endpoint /fund-details/<fund-slug>/ (Detalle de Subvención) ===")
    detalle_subvencion = asyncio.run(api.obtener_detalle_subvencion("ayudas-para-startups-tecnologicas-innovadoras-del-programa-neotec-ano-2024"))
    print("Detalle de la subvención:", detalle_subvencion)