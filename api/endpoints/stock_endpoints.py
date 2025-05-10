from typing import List, Dict, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from dependency_injector.wiring import inject, Provide

from models.stock_models import StockDataRequest, StockMetadata, OHLCVData
from services.stock_service import StockService
from api.api_structure import Container

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/{symbol}", summary="Get stock data")
@inject
async def get_stock_data(
    symbol: str,
    timeframe: str = "1d",
    service: StockService = Depends(Provide[Container.stock_service])
) -> Dict:
    """
    Get historical stock data for a specific symbol.
    
    Parameters:
    - **symbol**: Stock ticker symbol
    - **timeframe**: Data timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
    
    Returns:
    - Stock data with OHLCV values
    """
    try:
        return await service.get_stock_data(symbol, timeframe)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stock data: {str(e)}"
        )

@router.get("/search", summary="Search stocks")
@inject
async def search_stocks(
    query: Annotated[str, Query(min_length=2)],
    limit: int = 10,
    service: StockService = Depends(Provide[Container.stock_service])
) -> List[StockMetadata]:
    """
    Search for stocks by name or symbol.
    
    Parameters:
    - **query**: Search query (min 2 characters)
    - **limit**: Maximum number of results to return
    
    Returns:
    - List of matching stocks with metadata
    """
    try:
        return await service.search_stocks(query, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )