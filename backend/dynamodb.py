import boto3
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from boto3.dynamodb.conditions import Key

# Cargar variables de entorno
load_dotenv()

# Conexión con DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_DYNAMO_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Obtener la tabla de DynamoDB
TABLE_NAME = "chat_history"
table = dynamodb.Table(TABLE_NAME)

# def insert_chat_messages(user_id: str, conversation_id: str, messages: List[Dict[str, str]]):
#     """
#     Guarda múltiples mensajes en DynamoDB dividiéndolos en ítems individuales, evitando duplicados en la clave primaria.
#     """
#     print("guardando")
#     try:
#         existing_message_ids = set()  # Evita IDs duplicados

#         with table.batch_writer() as batch:
#             for idx, msg in enumerate(messages):
#                 message_id = str(uuid.uuid4())  # Generar un UUID único
#                 while message_id in existing_message_ids:  # Asegurar que sea único en la ejecución actual
#                     message_id = str(uuid.uuid4())

#                 existing_message_ids.add(message_id)  # Agregar a la lista de control

#                 item = {
#                     "userId": user_id,  # Clave de partición
#                     "conversationId": conversation_id,  # Clave de ordenación
#                     "messageId": message_id,  # ID único garantizado
#                     "conversation_date": msg.get("timestamp", datetime.now(timezone.utc).isoformat()),  # Marca de tiempo ISO 8601
#                     "role": msg.get("sender", "unknown"),  # "user" o "bot"
#                     "message_content": msg.get("text", ""),  # Contenido del mensaje
#                     "order": idx  # Para mantener orden de los mensajes
#                 }
#                 batch.put_item(Item=item)  # Guarda cada mensaje como un ítem separado
#                 print(f"✅ Mensaje insertado: {item}")

#         print("✅ Conversación guardada en DynamoDB correctamente")
#     except Exception as e:
#         print(f"❌ Error guardando la conversación en DynamoDB: {str(e)}")

def insert_chat_messages(user_id: str, conversation_id: str, messages: List[Dict[str, str]]):
    """
    Guarda múltiples mensajes en DynamoDB, con un tiempo de expiración automático.
    """
    print("Guardando con TTL activado")
    try:
        existing_message_ids = set()
        now = datetime.now(timezone.utc)
        expiration_time = int((now + timedelta(days=30)).timestamp())  # Conversaciones expiran en 30 días

        with table.batch_writer() as batch:
            for idx, msg in enumerate(messages):
                message_id = str(uuid.uuid4())
                while message_id in existing_message_ids:
                    message_id = str(uuid.uuid4())

                existing_message_ids.add(message_id)

                item = {
                    "userId": user_id,
                    "conversationId": conversation_id,
                    "messageId": message_id,
                    "conversation_date": msg.get("timestamp", now.isoformat()),
                    "role": msg.get("sender", "unknown"),
                    "message_content": msg.get("text", ""),
                    "order": idx,
                    "expirationTime": expiration_time  # Se usará para TTL
                }
                batch.put_item(Item=item)
                print(f"✅ Mensaje insertado: {item}")

        print("✅ Conversación guardada con TTL en DynamoDB correctamente")
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
    

def get_conversations(user_id: str) -> List[Dict]:
    """
    Obtiene los IDs únicos de las conversaciones de un usuario en DynamoDB.
    """
    try:
        response = table.query(
            KeyConditionExpression=Key("userId").eq(user_id),
            ProjectionExpression="conversationId, conversation_date"
        )

        # Extraer IDs únicos de las conversaciones
        unique_conversations = {}
        
        for conv in response.get("Items", []):
            conv_id = conv["conversationId"]
            if conv_id not in unique_conversations:
                unique_conversations[conv_id] = datetime.strptime(conv["conversation_date"][:16], "%Y-%m-%dT%H:%M").strftime("%d/%m/%Y %H:%M")

        # Convertimos a lista de diccionarios
        conversations = [
            {"conversationId": conv_id, "conversation_date": conv_date}
            for conv_id, conv_date in unique_conversations.items()
        ]

        return conversations

    except Exception as e:
        print(f"❌ Error obteniendo historial de conversaciones: {str(e)}")
        return []