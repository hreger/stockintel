class DataProviderManager:
    def __init__(self):
        self.providers = {
            'alpha_vantage': AlphaVantageProvider(),
            'polygon': PolygonProvider(),
            'yahoo_finance': YahooFinanceProvider()
        }
        
    def get_stock_data(self, symbol, provider_priority=['alpha_vantage', 'polygon']):
        """Fetch data from multiple providers with fallback"""
        for provider_name in provider_priority:
            try:
                provider = self.providers[provider_name]
                return provider.get_stock_data(symbol)
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {str(e)}")
                continue
                
        raise Exception("All providers failed to retrieve data")