import boto3
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import List, Dict

# Cargar variables de entorno
load_dotenv()

# Configurar conexión con DynamoDB usando `resource`
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_DYNAMO_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Obtener la tabla de DynamoDB
TABLE_NAME = "chat_history"
table = dynamodb.Table(TABLE_NAME)

def insert_chat_messages(user_id: str, conversation_id: str, messages: List[Dict[str, str]]):
    """
    Guarda múltiples mensajes en DynamoDB dividiéndolos en ítems individuales, evitando duplicados en la clave primaria.
    """
    try:
        existing_message_ids = set()  # 🔹 Evita IDs duplicados

        with table.batch_writer() as batch:
            for idx, msg in enumerate(messages):
                message_id = str(uuid.uuid4())  # Generar un UUID único
                while message_id in existing_message_ids:  # Asegurar que sea único en la ejecución actual
                    message_id = str(uuid.uuid4())

                existing_message_ids.add(message_id)  # Agregar a la lista de control

                item = {
                    "userId": user_id,  # Clave de partición
                    "conversationId": conversation_id,  # Clave de ordenación
                    "messageId": message_id,  # ID único garantizado
                    "timestamp": msg.get("timestamp", datetime.now(timezone.utc).isoformat()),  # Marca de tiempo ISO 8601
                    "role": msg.get("sender", "unknown"),  # "user" o "bot"
                    "message_content": msg.get("text", ""),  # Contenido del mensaje
                    "order": idx  # Para mantener orden de los mensajes
                }
                batch.put_item(Item=item)  # Guarda cada mensaje como un ítem separado
                print(f"✅ Mensaje insertado: {item}")

        print("✅ Conversación guardada en DynamoDB correctamente")
    except Exception as e:
        print(f"❌ Error guardando la conversación en DynamoDB: {str(e)}")


def get_chat_history(user_id: str) -> List[Dict]:
    """
    Obtiene el historial de una conversación específica de un usuario.
    """
    try:
        response = table.query(
            KeyConditionExpression="userId = :user_id",
            ExpressionAttributeValues={
                ":user_id": user_id,
            }
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"❌ Error obteniendo historial de chat: {str(e)}")
        return []

if __name__ == "__main__":
    print("🔍 Probando conexión con DynamoDB...")

    # Insertar mensajes de prueba
    test_messages = [
        {
            "sender": "bot",
            "text": "¡Hola! Soy un asistente virtual para ayudarte a encontrar subvenciones. Voy a hacerte algunas preguntas. Por favor, ¿podrías decirme en qué Comunidad Autónoma está el cliente ?"
        },
        {
            "sender": "user",
            "text": "kñkñl"
        },
        {
            "sender": "bot",
            "text": "¿Cuál es el tipo de empresa? (Autónomo, PYME, Gran Empresa)",
        },
        {
            "sender": "user",
            "text": "ñlñ"
        },
        {
            "sender": "bot",
            "text": ""
        }
    ]

    insert_chat_messages("user123", "conv-236", test_messages)

    # Recuperar los mensajes insertados
    history = get_chat_history("user123")
    print("\n🔍 Historial de la conversación obtenida desde DynamoDB:")
    for msg in history:
        print(msg)
