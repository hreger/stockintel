class APIRateLimiter:
    def __init__(self):
        self.last_call_time = {}  # Track by provider
        self.min_intervals = {
            'alpha_vantage': 12,  # 12 seconds between calls
            'polygon': 1,         # 1 second between calls
            'yahoo_finance': 2    # 2 seconds between calls
        }
        
    def wait_if_needed(self, provider: str):
        """Ensure minimum delay between API calls"""
        current_time = time.time()
        
        if provider not in self.last_call_time:
            self.last_call_time[provider] = current_time
            return
            
        elapsed = current_time - self.last_call_time[provider]
        min_interval = self.min_intervals.get(provider, 5)  # Default 5s
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
            
        self.last_call_time[provider] = time.time()