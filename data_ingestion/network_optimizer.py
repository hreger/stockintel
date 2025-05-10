import aiohttp
import asyncio
from typing import List, Dict

class NetworkOptimizer:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def init_session(self):
        """Initialize connection pool"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            
    async def fetch_data(self, urls: List[str]) -> List[Dict]:
        """Optimized parallel data fetching"""
        await self.init_session()
        async with self.session:
            tasks = [self.session.get(url) for url in urls]
            responses = await asyncio.gather(*tasks)
            return [await r.json() for r in responses]