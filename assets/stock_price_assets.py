import asyncio
from typing import List
from datetime import datetime
from dagster import asset

@asset(group_name="stocks")
def stock_symbols() -> List[str]:
    """Stock symbols to track"""
    return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]


@asset(group_name="stocks", deps=[stock_symbols])
def fetch_stock_prices(stock_symbols: List[str]):
    """Trigger price fetch tasks"""
    from app.main import app as celery_app_instance
    # Get the task from Celery app registry
    fetch_task = celery_app_instance.tasks.get('fetch_stock_price')
    if fetch_task:
        return [fetch_task.delay(symbol).id for symbol in stock_symbols]
    else:
        raise RuntimeError("Task 'fetch_stock_price' not found in Celery app")


# @asset(group_name="stocks", deps=[fetch_stock_prices])
# def stored_stock_prices(stock_symbols: List[str]):
#     """Verify prices stored in DB"""
#     from app.main import orm_app
    
#     collection = orm_app.get_collection("stock_prices")
#     today = datetime.now().date().isoformat()
    
#     # Motor (async MongoDB driver) requires async calls
#     return asyncio.run(collection.count_documents({
#         "symbol": {"$in": stock_symbols},
#         "date": today
#     }))
@asset(group_name="stocks", deps=[fetch_stock_prices])
async def stored_stock_prices(stock_symbols: List[str]):
    """Verify prices stored in DB"""
    from app.main import orm_app
    
    collection = orm_app.get_collection("stock_prices")
    today = datetime.now().date().isoformat()
    
    return await collection.count_documents({
        "symbol": {"$in": stock_symbols},
        "date": today
    })
