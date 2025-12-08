# price_app/services/stock_service.py (BUSINESS LOGIC)
import yfinance as yf
from datetime import datetime
from typing import Dict


def fetch_stock_price_data(symbol: str) -> Dict:
    """Fetch stock price from Yahoo Finance"""
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        return {"symbol": symbol, "status": "no_data"}

    latest = data.iloc[-1]

    return {
        "symbol": symbol,
        "date": datetime.now().date().isoformat(),
        "open": float(latest['Open']),
        "high": float(latest['High']),
        "low": float(latest['Low']),
        "close": float(latest['Close']),
        "volume": int(latest['Volume']),
        "fetched_at": datetime.now().isoformat(),
        "status": "success"
    }


def store_stock_price_data(price_data: Dict, collection) -> Dict:
    """Store stock price in MongoDB"""
    if price_data.get("status") != "success":
        return price_data

    result = collection.update_one(
        {"symbol": price_data["symbol"], "date": price_data["date"]},
        {"$set": price_data},
        upsert=True
    )

    return {
        "symbol": price_data["symbol"],
        "status": "stored",
        "price": price_data["close"],
        "upserted": result.upserted_id is not None
    }