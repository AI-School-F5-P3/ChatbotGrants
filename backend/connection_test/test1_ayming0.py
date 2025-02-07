import os
from dotenv import load_dotenv
import boto3

# Load environment variables from .env file
load_dotenv()

access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION')

# Create a session
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region
)

# Create a client using the session
s3_client = session.client('s3')

def list_s3_files(bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"File: {obj['Key']}, Size: {obj['Size']} bytes")
    else:
        print("No files found in the bucket.")

# Usage
bucket_name = 'repositorio-grantsbot'
list_s3_files(bucket_name)

def upload_file_to_s3(file_path, bucket_name, object_name=None):
    # If S3 object_name is not specified, use file_name
    if object_name is None:
        object_name = file_path.split('/')[-1]

    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File {file_path} uploaded successfully to {bucket_name}/{object_name}")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

# Usage
local_file_path = 'test_ak.pdf'
s3_bucket_name = 'repositorio-grantsbot'
s3_object_name = 'test_ak.pdf'  # Optional

upload_file_to_s3(local_file_path, s3_bucket_name, s3_object_name)

