import os
import json
import asyncio
from kafka import KafkaProducer
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv

load_dotenv()

class StockDataProducer:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.ts = TimeSeries(key=self.alpha_vantage_key, output_format='json')
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
    async def fetch_stock_data(self, symbol):
        """Fetch real-time stock data from Alpha Vantage"""
        try:
            data, _ = self.ts.get_quote_endpoint(symbol)
            return {
                'symbol': symbol,
                'price': float(data['05. price']),
                'volume': int(data['06. volume']),
                'timestamp': data['07. latest trading day']
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None

    async def produce_to_kafka(self, symbol):
        """Produce stock data to Kafka topic"""
        while True:
            data = await self.fetch_stock_data(symbol)
            if data:
                self.producer.send('stock_data', value=data)
                print(f"Produced data for {symbol}: {data}")
            await asyncio.sleep(60)  # Fetch data every minute

async def main():
    producer = StockDataProducer()
    symbols = ['AAPL', 'MSFT', 'GOOGL']  # Example symbols
    tasks = [producer.produce_to_kafka(symbol) for symbol in symbols]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 