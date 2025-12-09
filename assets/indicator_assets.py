# price_app/assets/indicator_assets.py
from dagster import asset, get_dagster_logger
from app.main import app as celery_app
from typing import Dict, List

@asset(group_name="indicators")
def indicator_config():
    return {
        "collections": {
            "AAPL": "AAPL_factors",
            "GOOGL": "GOOGL_factors",
            "MSFT": "MSFT_factors",
            "TSLA": "TSLA_factors",
        }
    }

@asset(group_name="indicators")
def queue_indicator_computation(fetch_stock_prices: Dict[str, str], indicator_config) -> Dict[str, str]:
    logger = get_dagster_logger()
    task_ids = {}
    
    for symbol, fetch_task_id in fetch_stock_prices.items():
        try:
            price_data = celery_app.AsyncResult(fetch_task_id).get(timeout=180)
            if price_data.get("status") == "success":
                result = celery_app.send_task(
                    "tasks.indicator_tasks.compute_indicators",
                    args=[symbol, price_data["records"]]
                )
                task_ids[symbol] = result.id
                logger.info(f"Queued indicators for {symbol}: {result.id}")
        except Exception as e:
            logger.error(f"Failed to queue indicators for {symbol}: {e}")
    
    return task_ids

@asset(group_name="indicators")
def store_indicators(queue_indicator_computation: Dict[str, str], indicator_config) -> Dict:
    logger = get_dagster_logger()
    results = {}
    
    for symbol, task_id in queue_indicator_computation.items():
        try:
            data = celery_app.AsyncResult(task_id).get(timeout=300)
            collection_name = indicator_config["collections"].get(symbol, f"{symbol}_factors")
            store_task = celery_app.send_task(
                "tasks.indicator_tasks.store_indicators",
                args=[data, collection_name]
            )
            results[symbol] = store_task.id
        except Exception as e:
            results[symbol] = None
            logger.error(f"Indicator storage failed for {symbol}: {e}")
    
    return results