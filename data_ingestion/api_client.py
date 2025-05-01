import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv
from data_ingestion.database import StockData, get_db, init_db
import time
import json
from pathlib import Path

class StockDataClient:
    def __init__(self):
        load_dotenv()
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        self.cache_dir = Path('data_cache')
        self.cache_dir.mkdir(exist_ok=True)
        init_db()

    def _get_cache_path(self, symbol: str, timeframe: str) -> Path:
        return self.cache_dir / f"{symbol}_{timeframe}.json"

    def _save_to_cache(self, symbol: str, timeframe: str, data: dict):
        cache_path = self._get_cache_path(symbol, timeframe)
        with open(cache_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': data
            }, f)

    def _load_from_cache(self, symbol: str, timeframe: str) -> Optional[dict]:
        cache_path = self._get_cache_path(symbol, timeframe)
        if not cache_path.exists():
            return None
        
        with open(cache_path, 'r') as f:
            cached = json.load(f)
            cache_time = datetime.fromisoformat(cached['timestamp'])
            # Cache valid for 1 day
            if datetime.now() - cache_time < timedelta(days=1):
                return cached['data']
        return None

    def get_historical_data(self, symbol: str, timeframe: str = '1D') -> pd.DataFrame:
        """
        Get historical stock data based on timeframe with caching
        """
        try:
            # Try to get data from cache first
            cached_data = self._load_from_cache(symbol, timeframe)
            if cached_data:
                print(f"Using cached data for {symbol}")
                data = cached_data
            else:
                # Set up the API parameters based on timeframe
                if timeframe == '1D':
                    params = {
                        "function": "TIME_SERIES_INTRADAY",
                        "symbol": symbol,
                        "interval": "5min",
                        "apikey": self.alpha_vantage_key,
                        "outputsize": "full"
                    }
                    time_series_key = "Time Series (5min)"
                else:
                    params = {
                        "function": "TIME_SERIES_DAILY",
                        "symbol": symbol,
                        "apikey": self.alpha_vantage_key,
                        "outputsize": "full"
                    }
                    time_series_key = "Time Series (Daily)"

                # Add delay to respect rate limits
                time.sleep(12)
                
                response = requests.get(self.base_url, params=params)
                data = response.json()
                
                if "Error Message" in data or "Information" in data or time_series_key not in data:
                    print(f"API Response for {symbol}: {data}")
                    # Try to use cached data even if expired
                    cached_data = self._load_from_cache(symbol, timeframe)
                    if cached_data:
                        print(f"Using expired cache for {symbol} due to API limit")
                        data = cached_data
                    else:
                        return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
                else:
                    # Save valid response to cache
                    self._save_to_cache(symbol, timeframe, data)

            # Process the data
            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            
            # Rename columns to match expected format
            column_map = {
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
                '5. volume': 'volume'
            }
            df = df.rename(columns=column_map)
            
            # Convert string values to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            # Filter data based on timeframe
            now = datetime.now()
            if timeframe == '1D':
                start_date = now - timedelta(days=1)
            elif timeframe == '1W':
                start_date = now - timedelta(weeks=1)
            elif timeframe == '1M':
                start_date = now - timedelta(days=30)
            else:  # 1Y
                start_date = now - timedelta(days=365)
            
            df = df[df.index >= start_date]
            
            return df.sort_index()
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])