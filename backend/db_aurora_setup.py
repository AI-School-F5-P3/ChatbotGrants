import boto3
import os
from dotenv import load_dotenv
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class AuroraDBSetup:
    def __init__(self):
        load_dotenv()
        
        # Configuración de AWS
        self.rds_client = boto3.client('rds',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        # Configuración Aurora
        self.CLUSTER_IDENTIFIER = os.getenv('AURORA_CLUSTER_IDENTIFIER')
        self.DB_NAME = os.getenv('DB_NAME')
        
    def create_funds_table(self):
        CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS funds (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fund_id VARCHAR(255) UNIQUE,
            is_open BOOLEAN,
            search_by_text TEXT,
            max_budget DECIMAL(15,2),
            max_total_amount DECIMAL(15,2),
            min_total_amount DECIMAL(15,2),
            bdns TEXT,
            office TEXT,
            start_date DATE,
            end_date DATE,
            final_period_end_date DATE,
            final_period_start_date DATE,
            search_tab INTEGER,
            provinces JSON,
            applicants JSON,
            communities JSON,
            action_items JSON,
            origins JSON,
            activities JSON,
            region_types JSON,
            types JSON,
            details JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_fund_is_open (is_open),
            INDEX idx_fund_dates (start_date, end_date)
        )
        """
        
        try:
            # Obtener endpoint del cluster
            response = self.rds_client.describe_db_clusters(
                DBClusterIdentifier=self.CLUSTER_IDENTIFIER
            )
            endpoint = response['DBClusters'][0]['Endpoint']
            
            # Conectar y crear tabla
            conn = mysql.connector.connect(
                host=endpoint,
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=self.DB_NAME
            )
            
            with conn.cursor() as cursor:
                cursor.execute(CREATE_TABLE_SQL)
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error creando tabla en Aurora: {str(e)}")
            raise