import pandas as pd
from sqlalchemy import func
from data_ingestion.database import StockData, get_db

def check_data_status():
    """Check the status of collected data"""
    db = next(get_db())
    try:
        # Get count by symbol
        counts = (
            db.query(StockData.symbol, func.count(StockData.id))
            .group_by(StockData.symbol)
            .all()
        )
        
        # Get date range by symbol
        for symbol, count in counts:
            date_range = (
                db.query(
                    func.min(StockData.timestamp),
                    func.max(StockData.timestamp)
                )
                .filter(StockData.symbol == symbol)
                .first()
            )
            
            print(f"\nSymbol: {symbol}")
            print(f"Data points: {count}")
            print(f"Date range: {date_range[0]} to {date_range[1]}")

if __name__ == "__main__":
    check_data_status() 