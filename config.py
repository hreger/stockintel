import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
POLYGON_KEY = os.getenv('POLYGON_KEY')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'stock_data'

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'stockintel')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Model Configuration
ARIMA_ORDER = tuple(map(int, os.getenv('ARIMA_ORDER', '5,1,0').split(',')))
PREDICTION_STEPS = int(os.getenv('PREDICTION_STEPS', '7'))

# Scraper Configuration
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))