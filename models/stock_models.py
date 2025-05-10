from typing import Dict, List, Optional, Union, Literal, TypedDict, Protocol
from datetime import datetime
from pydantic import BaseModel, Field, validator

# Type definitions
TimeframeType = Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]

class OHLCVData(TypedDict):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockMetadata(TypedDict):
    symbol: str
    name: str
    exchange: str
    sector: Optional[str]
    industry: Optional[str]

# Protocol for data providers
class DataProvider(Protocol):
    def get_stock_data(self, symbol: str, timeframe: TimeframeType) -> List[OHLCVData]:
        ...
    
    def get_stock_metadata(self, symbol: str) -> StockMetadata:
        ...

# Pydantic models for validation
class StockDataRequest(BaseModel):
    symbol: str
    timeframe: TimeframeType = "1d"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('symbol')
    def validate_symbol(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Symbol must be a non-empty string")
        return v.upper()