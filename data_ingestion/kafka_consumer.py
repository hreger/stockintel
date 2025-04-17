import json
import os
from datetime import datetime
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import StockData, get_db, init_db

# Load environment variables
load_dotenv()

class StockDataConsumer:
    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.consumer = KafkaConsumer(
            'stock_data',
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        
        # Initialize database
        init_db()
    
    def process_message(self, message, db: Session):
        """Process a single Kafka message and store it in the database"""
        try:
            data = message.value
            stock_data = StockData(
                symbol=data['symbol'],
                price=data['price'],
                volume=data['volume'],
                timestamp=datetime.fromisoformat(data['timestamp'])
            )
            
            db.add(stock_data)
            db.commit()
            print(f"Processed data for {data['symbol']}: {data}")
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            db.rollback()
    
    def consume_data(self):
        """Consume stock data from Kafka and store it in the database"""
        db = next(get_db())
        try:
            for message in self.consumer:
                self.process_message(message, db)
        except KeyboardInterrupt:
            print("Stopping consumer...")
        finally:
            db.close()
            self.consumer.close()

if __name__ == "__main__":
    consumer = StockDataConsumer()
    consumer.consume_data() 