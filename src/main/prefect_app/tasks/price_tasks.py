import requests
import os
from typing import List, Dict
from prefect import task
from datetime import datetime


@task(name="fetch_raw_prices")
def fetch_raw_prices(limit: int = 100) -> List[Dict]:
    """
    Fetch raw prices using requests to call https://jsonplaceholder.typicode.com/posts with _limit.
    Returns a list of dicts shaped like price data: symbol, price, volume, timestamp, metadata.
    """
    url = f"https://jsonplaceholder.typicode.com/posts?_limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    
    # Transform posts data to price-like data
    raw_prices = []
    for i, post in enumerate(response.json()):
        price_data = {
            "symbol": f"SYM{i:03d}",
            "price": float(100 + (i % 100)),
            "volume": int(1000 + (i * 100)),
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "title": post.get("title", ""),
                "userId": post.get("userId", 0)
            }
        }
        raw_prices.append(price_data)
    
    return raw_prices


@task(name="compute_indicators")
def compute_indicators(raw_prices: List[Dict]) -> List[Dict]:
    """
    Computes simple SMA/EMA style indicators using pure Python.
    Adds them into each dict as new keys.
    Must NOT import from dagster_app or any Dagster tasks.
    """
    if not raw_prices:
        return raw_prices
    
    # Calculate simple moving average (SMA) over last 5 prices
    # and exponential moving average (EMA) with smoothing factor 0.3
    results = []
    
    for i, price_data in enumerate(raw_prices):
        # Copy the original data
        result = price_data.copy()
        
        # Simple Moving Average (SMA) - average of last 5 prices (or all if less than 5)
        sma_window = min(5, i + 1)
        sma_sum = sum(raw_prices[j]["price"] for j in range(i - sma_window + 1, i + 1))
        sma = sma_sum / sma_window
        
        # Exponential Moving Average (EMA) - with smoothing factor 0.3
        if i == 0:
            ema = price_data["price"]
        else:
            ema = 0.3 * price_data["price"] + 0.7 * results[i-1].get("ema", price_data["price"])
        
        # Add indicators to the result
        result["sma"] = round(sma, 2)
        result["ema"] = round(ema, 2)
        
        results.append(result)
    
    return results


@task(name="store_results")
def store_results(results: List[Dict]) -> int:
    """
    Stores data into MongoDB using either pymongo or the mongo_connection library.
    Uses env vars with defaults:
    MONGODB_URI = mongodb://localhost:27017/
    MONGODB_DB_NAME = price_app
    MONGODB_COLLECTION_NAME = prices_prefect
    Returns the number of inserted documents and prints a short log.
    """
    # Get environment variables with defaults
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB_NAME", "price_app")
    collection_name = os.getenv("MONGODB_COLLECTION_NAME", "prices_prefect")
    
    try:
        # Try to use mongo_connection library first
        from mongo_connection.src.mongo_connection.app import MongoConnection
        mongo_conn = MongoConnection(mongodb_uri)
        db = mongo_conn.client[db_name]
        collection = db[collection_name]
        inserted_count = len(results)
        if results:
            collection.insert_many(results)
        print(f"Stored {inserted_count} price records in MongoDB collection '{collection_name}'")
        return inserted_count
    except ImportError:
        # Fallback to pymongo if mongo_connection is not available
        try:
            from pymongo import MongoClient
            client = MongoClient(mongodb_uri)
            db = client[db_name]
            collection = db[collection_name]
            inserted_count = len(results)
            if results:
                collection.insert_many(results)
            print(f"Stored {inserted_count} price records in MongoDB collection '{collection_name}'")
            return inserted_count
        except ImportError:
            # If neither library is available, just print the results
            print(f"MongoDB libraries not available. Would have stored {len(results)} records:")
            for result in results[:3]:  # Print first 3 for brevity
                print(f"  - {result['symbol']}: ${result['price']} (SMA: {result.get('sma', 'N/A')}, EMA: {result.get('ema', 'N/A')})")
            print(f"  ... and {max(0, len(results) - 3)} more")
            return len(results)