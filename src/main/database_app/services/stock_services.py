# # servers/services/stock_service.py (BUSINESS LOGIC)
import yfinance as yf
from datetime import datetime
from typing import Dict
import asyncio

_event_loop = None

def fetch_stock_price_data(symbol: str, start_date: str = None, end_date: str = None) -> Dict:
    """Fetch stock prices from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        
        records = []
        for date, row in data.iterrows():
            records.append({
                "symbol": symbol,
                "date": str(date.date()),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']),
                "fetched_at": datetime.now().isoformat(),
            })
        
        return { "symbol": symbol, "records": records, "count": len(records), "status": "success" }
        
    except Exception as e:
        return f"data fetch error for {symbol}: {str(e)}"

def _get_event_loop():
    """Get or create event loop for the worker process"""
    global _event_loop
    try:
        _event_loop = asyncio.get_running_loop()
    except RuntimeError:
        if _event_loop is None or _event_loop.is_closed():
            _event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_event_loop)
    return _event_loop

def store_stock_price_data(price_data: Dict, collection) -> Dict:
    """Store stock prices to MongoDB - ASYNC with event loop reuse"""
    symbol = price_data.get("symbol", "UNKNOWN")
    
    if price_data.get("status") != "success":
        return { "symbol": symbol, "status": "skipped", "count": 0, "reason": price_data.get("status") }
    
    records = price_data.get("records", [])
    if not records:
        return { "symbol": symbol, "status": "no_records", "count": 0 }
    try:
        loop = _get_event_loop()
        result = loop.run_until_complete(_store_records_async(symbol, records, collection))
        return result
        
    except Exception as e:
        return f"data store error for {symbol}: {str(e)}"

async def _store_records_async(symbol: str, records: list, collection) -> Dict:
    """Async helper to store records"""
    inserted = 0
    
    for record in records:
        try:
            await collection.update_one(
                {"symbol": record["symbol"], "date": record["date"]},
                {"$set": record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            continue
    
    return { "symbol": symbol, "status": "success", "count": inserted, "total": len(records)}
