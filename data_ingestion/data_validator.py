from pydantic import BaseModel, validator, Field
from typing import List, Dict, Optional
from datetime import datetime

class OHLCVData(BaseModel):
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    
    @validator('high')
    def high_greater_than_low(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError('high must be greater than or equal to low')
        return v
        
    @validator('high', 'low')
    def validate_range(cls, v, values):
        if 'open' in values:
            # Validate reasonable price movement (e.g., not >50% from open)
            if v > values['open'] * 1.5 or v < values['open'] * 0.5:
                raise ValueError('Price movement exceeds reasonable range')
        return v

class DataValidator:
    def validate_stock_data(self, data: List[Dict]) -> List[OHLCVData]:
        """Validate and clean stock data"""
        validated_data = []
        errors = []
        
        for item in data:
            try:
                validated_item = OHLCVData(**item)
                validated_data.append(validated_item)
            except Exception as e:
                errors.append({"item": item, "error": str(e)})
                
        if errors:
            # Log errors but continue with valid data
            print(f"Validation errors: {len(errors)} out of {len(data)} records")
            
        return validated_data