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
ARIMA_ORDER = (5, 1, 0)  # (p, d, q) parameters for ARIMA model
PREDICTION_STEPS = 7  # Number of days to predict

# Scraper Configuration
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3 