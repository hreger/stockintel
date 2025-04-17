import os
import json
import time
from datetime import datetime
from typing import Dict, List
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class StockDataProducer:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        if not self.alpha_vantage_key:
            raise ValueError("ALPHA_VANTAGE_KEY not found in environment variables")
            
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        
        logger.info(f"Initializing producer with bootstrap servers: {self.kafka_bootstrap_servers}")
        
        # Initialize Kafka producer
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda v: v.encode('utf-8')
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            raise
    
    def fetch_stock_data(self, symbol: str) -> Dict:
        """Fetch stock data from Alpha Vantage API"""
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',  # Changed to GLOBAL_QUOTE for simpler, more reliable data
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        
        try:
            logger.info(f"Fetching data for {symbol}")
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': symbol,
                    'price': float(quote['05. price']),
                    'volume': int(quote['06. volume']),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                error_message = data.get('Note', data.get('Error Message', 'Unknown error'))
                logger.error(f"Error fetching data for {symbol}: {error_message}")
                if 'Note' in data:  # API rate limit message
                    logger.warning("API rate limit reached. Waiting for 60 seconds...")
                    time.sleep(60)
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception while fetching data for {symbol}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Exception while fetching data for {symbol}: {str(e)}")
            return None
    
    def produce_data(self):
        """Produce stock data to Kafka topic"""
        logger.info("Starting data production...")
        while True:
            for symbol in self.symbols:
                data = self.fetch_stock_data(symbol)
                if data:
                    try:
                        self.producer.send(
                            'stock_data',
                            key=symbol,
                            value=data
                        )
                        logger.info(f"Produced data for {symbol}: {data}")
                    except Exception as e:
                        logger.error(f"Error producing data for {symbol}: {str(e)}")
            
            # Wait for 1 minute before next fetch to respect API rate limits
            logger.info("Waiting 60 seconds before next fetch...")
            time.sleep(60)

if __name__ == "__main__":
    try:
        producer = StockDataProducer()
        producer.produce_data()
    except KeyboardInterrupt:
        logger.info("Shutting down producer...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise 