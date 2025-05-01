import requests
from typing import Dict, List
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from database import StockData, get_db, init_db

load_dotenv()

class StockDataClient:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        init_db()
        
    def get_stock_data(self, symbol: str) -> Dict:
        """Get real-time stock data and store it directly"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            stock_data = {
                'symbol': symbol,
                'price': float(quote['05. price']),
                'volume': int(quote['06. volume']),
                'timestamp': datetime.now()
            }
            
            # Store data directly in database
            self._store_data(stock_data)
            return stock_data
        return None
    
    def _store_data(self, data: Dict):
        """Store stock data directly in database"""
        db = next(get_db())
        try:
            stock_data = StockData(
                symbol=data['symbol'],
                price=data['price'],
                volume=data['volume'],
                timestamp=data['timestamp']
            )
            db.add(stock_data)
            db.commit()
        except Exception as e:
            logging.error(f"Error storing data: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def fetch_all_symbols(self):
        """Fetch data for all symbols"""
        for symbol in self.symbols:
            try:
                data = self.get_stock_data(symbol)
                if data:
                    logging.info(f"Fetched and stored data for {symbol}: {data}")
            except Exception as e:
                logging.error(f"Error processing {symbol}: {str(e)}")

if __name__ == "__main__":
    client = StockDataClient()
    client.fetch_all_symbols()