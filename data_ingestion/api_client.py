import requests
import os

class StockDataClient:
    """
    A simple client to fetch stock data from Alpha Vantage or other APIs.
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_KEY")
        self.base_url = "https://www.alphavantage.co/query"

    def get_daily_time_series(self, symbol, outputsize="compact"):
        """
        Fetch daily time series data for a given stock symbol.
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": outputsize
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched data for {symbol}: {data}")  # Add this line for debugging
        return data

    # Add more methods as needed for your project