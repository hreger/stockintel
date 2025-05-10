from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.endpoints import stock_endpoints, portfolio_endpoints, analysis_endpoints
from api.error_handler import register_exception_handlers
from api.api_structure import lifespan

app = FastAPI(
    title="StockIntel API",
    description="""
    StockIntel provides financial market data and analysis tools.
    
    ## Features
    
    * Real-time and historical market data
    * Technical analysis indicators
    * Portfolio management
    * Price predictions
    * Sentiment analysis
    
    ## Authentication
    
    All API requests require an API key to be provided in the header.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Register middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Register routers
app.include_router(stock_endpoints.router)
app.include_router(portfolio_endpoints.router)
app.include_router(analysis_endpoints.router)

# Customize OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="StockIntel API",
        version="1.0.0",
        description="Financial market data and analysis API",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi