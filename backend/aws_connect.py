import os
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv
import boto3
from datetime import datetime, timedelta
import traceback
from boto3.dynamodb.conditions import Key, Attr

# Load environment variables
load_dotenv()

def get_temporary_credentials(duration: int = 3600):
    """Get temporary AWS credentials."""
    try:
        sts_client = boto3.client("sts")
        response = sts_client.get_session_token(DurationSeconds=duration)
        creds = response["Credentials"]
        return {
            "aws_access_key_id": creds["AccessKeyId"],
            "aws_secret_access_key": creds["SecretAccessKey"],
            "aws_session_token": creds["SessionToken"]
        }
    except Exception as e:
        print(f"Error getting temporary credentials: {e}")
        raise

def get_aws_session():
    """Create and return an AWS session with temporary credentials."""
    temp_creds = get_temporary_credentials()
    return boto3.Session(
        aws_access_key_id=temp_creds["aws_access_key_id"],
        aws_secret_access_key=temp_creds["aws_secret_access_key"],
        aws_session_token=temp_creds["aws_session_token"],
        region_name=os.getenv('AWS_REGION', 'eu-south-2')
    )

def get_bedrock_response(prompt: str):
    """Get response from Bedrock."""
    session = get_aws_session()
    
    bedrock = session.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION')
    )
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.5
    }
    
    try:
        response = bedrock.invoke_model(
            modelId='eu.anthropic.claude-3-5-sonnet-20240620-v1:0',
            accept='application/json',
            contentType='application/json',
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    


# CHINOS



class DynamoDBManager:
    def __init__(self, table_name: str = 'grantsbot', region: str = 'eu-south-2'):
        """Initialize DynamoDB manager with table."""
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def write_chat_history(self, user_id: str, chat_id: str, message: dict) -> bool:
        """Write a chat message to DynamoDB."""
        try:
            timestamp = datetime.utcnow().isoformat()
            primary_key = f"chat_{user_id}_{chat_id}_{timestamp}"
            
            item = {
                'grantsbot': user_id,  # Partition key
                'primary_key': primary_key,  # Sort key
                'timestamp': timestamp,
                'message_content': message.get('content', ''),
                'role': message.get('role', 'user'),
                'metadata': message.get('metadata', {})
            }

            print(f"\n[Debug] Writing item to DynamoDB: {item}")
            response = self.table.put_item(Item=item)

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print("[Success] Item written successfully.")
                return True
            else:
                print(f"[Error] Unexpected response: {response}")
                return False

        except Exception as e:
            print(f"[Error] Failed to write to DynamoDB: {str(e)}")
            print(traceback.format_exc())
            return False

    def debug_scan_table(self):
        """Retrieve all records for debugging purposes."""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            print(f"\n[Debug] Table Scan Results ({len(items)} items found):")
            for item in items:
                print(item)
            return items
        except Exception as e:
            print(f"[Error] Scan failed: {str(e)}")
            print(traceback.format_exc())
            return []

    def get_chat_history(self, user_id: str, chat_id: str) -> list:
        """Retrieve chat history for a specific user and chat."""
        try:
            # Query based on partition key (user_id) and filter by chat_id
            response = self.table.query(
                KeyConditionExpression=Key('grantsbot').eq(user_id),
                FilterExpression=Attr('primary_key').begins_with(f"chat_{user_id}_{chat_id}"),
                ScanIndexForward=True  # Sort by timestamp ascending
            )

            items = response.get('Items', [])
            print(f"\n[Debug] Retrieved {len(items)} messages for user {user_id}, chat {chat_id}.")
            return items

        except Exception as e:
            print(f"[Error] Failed to retrieve chat history: {str(e)}")
            print(traceback.format_exc())
            return []

    def get_user_state(self, user_id: str, chat_id: str) -> Optional[Dict]:
        """Retrieve the latest user state from DynamoDB."""
        try:
            # Retrieve all state updates for the session
            response = self.table.query(
                KeyConditionExpression=Key('grantsbot').eq(user_id),
                FilterExpression=Attr('primary_key').begins_with(f"chat_{user_id}_{chat_id}") & 
                               Attr('role').eq('system') & 
                               Attr('message_content').eq('state_update'),
                ScanIndexForward=False  # Sort by timestamp descending (latest first)
            )

            items = response.get('Items', [])
            if items:
                print(f"\n[Debug] Retrieved latest state for user {user_id}, chat {chat_id}.")
                return items[0]['metadata']['state']
            else:
                print(f"\n[Debug] No state found for user {user_id}, chat {chat_id}.")
                return None

        except Exception as e:
            print(f"[Error] Failed to retrieve user state: {str(e)}")
            print(traceback.format_exc())
            return None