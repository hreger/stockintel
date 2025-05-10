class DataManager:
    def __init__(self):
        self.eod_cache = {}
        self.realtime_symbols = set()  # Priority symbols for real-time updates
        
    def get_stock_data(self, symbol, require_realtime=False):
        """Hybrid data retrieval strategy"""
        if not require_realtime and symbol in self.eod_cache:
            return self.eod_cache[symbol]
            
        if symbol in self.realtime_symbols:
            return self.get_realtime_data(symbol)
            
        return self.get_eod_data(symbol)