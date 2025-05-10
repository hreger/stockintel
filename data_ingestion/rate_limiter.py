class APIRateLimiter:
    def __init__(self):
        self.last_call_time = 0
        self.min_interval = 12  # seconds between calls
        
    def wait_if_needed(self):
        """Ensure minimum delay between API calls"""
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
            
        self.last_call_time = time.time()