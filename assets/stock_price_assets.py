# assets/stock_price_assets.py

from typing import Dict
from dagster import asset, get_dagster_logger
from app.main import app as celery_app
from omegaconf import OmegaConf

cfg = OmegaConf.load("config/config.yaml")

@asset(group_name="stocks")
def stock_config() -> Dict:
    """Stock fetch configuration - CONFIGURABLE"""
    return {
        "symbols": list(cfg.symbols),
        "start_date": cfg.start_date,
        "end_date": cfg.end_date
    }

@asset(group_name="stocks", auto_materialize_policy=None)
def fetch_stock_prices(stock_config: Dict) -> Dict[str, str]:
    """Queue fetch tasks for all stock symbols"""
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
    logger = get_dagster_logger()
    store_results = {}
    
    if not fetch_stock_prices:
        return store_results
    
    for symbol, task_id in fetch_stock_prices.items():
        try:
            # Wait for fetch task to complete
            price_data = celery_app.AsyncResult(task_id).get(timeout=120)
            
            # Check if fetch was successful
            if not price_data or price_data.get("status") != "success":
                logger.warning(f"Fetch failed for {symbol}")
                store_results[symbol] = None
                continue
            
            # Queue store task - pass symbol, task will use naming convention
            result = celery_app.send_task(
                'tasks.stock_tasks.store_stock_price',
                args=[price_data, symbol]  # Task receives price_data and symbol
            )
            store_results[symbol] = result.id
            logger.info(f"Queued store for {symbol} -> {result.id}")
            
        except Exception as e:
            logger.error(f"Error queuing store for {symbol}: {e}")
            store_results[symbol] = None
    
    return store_results