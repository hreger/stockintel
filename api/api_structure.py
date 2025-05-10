from typing import Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from dependency_injector import containers, providers
from contextlib import asynccontextmanager

# API Models
class StockDataRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1d"
    
class StockDataResponse(BaseModel):
    symbol: str
    data: List[Dict]
    metadata: Dict

# Dependency Container
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Services
    stock_client = providers.Singleton(
        StockDataClient,
        api_key=config.api_key
    )
    
    portfolio_service = providers.Singleton(
        PortfolioService,
        stock_client=stock_client
    )

# Application startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting StockIntel API")
    yield
    # Shutdown logic
    print("Shutting down StockIntel API")

# Create FastAPI application
app = FastAPI(
    title="StockIntel API",
    description="Financial market data and analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# Dependency injection
container = Container()
container.config.api_key.from_env("ALPHA_VANTAGE_KEY")

def get_stock_client():
    return container.stock_client()

def get_portfolio_service():
    return container.portfolio_service()