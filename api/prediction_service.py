from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import uvicorn
import logging
import sys
import os


# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.price_predictor import PricePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StockIntel Prediction API")
predictor = PricePredictor()

class PredictionRequest(BaseModel):
    symbol: str
    days: int = 5

class PredictionResponse(BaseModel):
    symbol: str
    predictions: List[Dict[str, Any]]  
    timestamp: datetime
    model_version: str = "1.0.0"


@app.get("/")
async def root():
    logger.info("Health check endpoint called")
    return {"status": "ok", "service": "StockIntel Prediction API"}

@app.post("/predict", response_model=PredictionResponse)
async def get_prediction(request: PredictionRequest):
    try:
        logger.info(f"Prediction requested for symbol: {request.symbol}")
        # Get predictions
        predictions_df = predictor.predict(request.symbol, days=request.days)
        
        # Format predictions
        predictions = [
            {
                "date": row['date'].isoformat(),
                "price": float(row['predicted_price'])
            }
            for _, row in predictions_df.iterrows()
        ]
        
        logger.info(f"Successfully generated predictions for {request.symbol}")
        return PredictionResponse(
            symbol=request.symbol,
            predictions=predictions,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error generating predictions for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/symbols")
async def get_available_symbols():
    try:
        model_files = os.listdir('models/saved_models')
        symbols = list(set([f.split('_')[0] for f in model_files if f.endswith('_model.h5')]))
        logger.info(f"Found {len(symbols)} available symbols")
        return {"symbols": symbols}
    except Exception as e:
        logger.error(f"Error listing symbols: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting StockIntel Prediction API...")
    uvicorn.run(
        app,
        host="127.0.0.1",  # Changed from 0.0.0.0 to localhost
        port=8000,
        log_level="info"
    ) 