from kafka import KafkaConsumer, KafkaProducer
import json
from typing import Callable

class StreamProcessor:
    def __init__(self, bootstrap_servers: List[str]):
        self.consumer = KafkaConsumer(
            'market_data',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
    def process_stream(self, processor_func: Callable):
        """Process streaming data in real-time"""
        for message in self.consumer:
            processed_data = processor_func(message.value)
            self.producer.send('processed_data', processed_data)