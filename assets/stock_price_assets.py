import asyncio
from typing import List, Dict
from datetime import datetime
from dagster import asset, get_dagster_logger
from app.main import orm_app
from app.main import app as celery_app

@asset(group_name="stocks")
def stock_config() -> Dict:
    """Stock fetch configuration - CONFIGURABLE"""
    return {
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN","NFLX","FB","NVDA","BABA","INTC","TCS"],
        "start_date": "2021-12-01",
        "end_date": "2025-12-01"
    }

@asset(group_name="stocks")
def fetch_stock_prices(stock_config: Dict) -> Dict[str, str]:
    logger = get_dagster_logger()   
    task_ids = {}
    for symbol in stock_config["symbols"]:
        result = celery_app.send_task(
            'tasks.stock_tasks.fetch_stock_price',
            args=[symbol, stock_config["start_date"], stock_config["end_date"]]
        )
        task_ids[symbol] = result.id
        logger.info(f"Queued fetch: {symbol} -> {result.id}")
    return task_ids

@asset(group_name="stocks")
def store_stock_prices(fetch_stock_prices: Dict[str, str]) -> Dict:
    """Dagster asset to queue storage tasks for all tickers"""
    store_results = {}
    if not fetch_stock_prices:
        return store_results
    
    for symbol, task_id in fetch_stock_prices.items():
        try:
            price_data = celery_app.AsyncResult(task_id).get(timeout=120)
            if not price_data or price_data.get("status") != "success":
                store_results[symbol] = None
                continue
            result = celery_app.send_task('tasks.stock_tasks.store_stock_price', args=[price_data, f"{symbol}_prices"])
            store_results[symbol] = result.id
        except Exception as e:
            store_results[symbol] = None
    return store_results
