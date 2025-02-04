import requests
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def register_sandbox_user():
    url = "https://sandbox.api.test.fandit.es/api/v1/users/partners-brand/registration/"
    headers = {
        'api-key': '2f8abdf6-0b87-4502-9c1d-79c52794e3fc',
        'Content-Type': 'application/json'
    }
    
    # Datos de registro - modifica estos valores
    data = {
        "email": "avkavrecic@gmail.com",  # tu email
        "first_name": "Angela",
        "password1": "Fandit1234",  # elige una contraseña
        "password2": "Fandit1234",  # la misma contraseña
        "platform": "traveltooleservices"
    }
    
    try:
        logger.info(f"Intentando registrar usuario con email: {data['email']}")
        response = requests.post(url, json=data, headers=headers)
        
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Respuesta: {response.text}")
        
        if response.status_code == 201:
            logger.info("Usuario registrado exitosamente")
            logger.info("Guarda estas credenciales para usarlas en tu archivo .env")
        else:
            logger.error("Error en el registro")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    register_sandbox_user()