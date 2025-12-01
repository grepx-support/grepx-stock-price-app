"""Dagster asset for close price download orchestration."""

from dagster import asset
from omegaconf import OmegaConf
from price_app.config.paths import DAGSTER_CONFIG
from app.celery_framework_app import app as celery_app
from db.MongoDBManager import MongoDBManager


_cfg = OmegaConf.load(DAGSTER_CONFIG)

SYMBOLS = _cfg.assets.config.close_price_download.symbols
TASK_NAME = _cfg.assets.config.close_price_download.celery_task
TIMEOUT = _cfg.assets.config.close_price_download.timeout


@asset(group_name="stock_data")
def close_price_download():
    """Trigger Celery tasks and store results in MongoDB."""
    results = []

    print(f"Starting close_price_download asset")
    print(f"SYMBOLS: {list(SYMBOLS)}")
    print(f"TASK_NAME: {TASK_NAME}")
    print(f"TIMEOUT: {TIMEOUT}")

    for symbol in SYMBOLS:
        print(f"Sending task for symbol: {symbol}")
        task = celery_app.send_task(TASK_NAME, args=[symbol])
        print(f"Task sent with ID: {task.id}")
        result = task.get(TIMEOUT)
        print(f"Result received for {symbol}: {result}")
        results.append(result)

    print(f"All tasks completed. Total results: {len(results)}")
    stored = MongoDBManager.get_prices()
    print(f"Stored records in DB: {len(stored)}")

    return {
        "downloaded": len(results),
        "stored_count": len(stored),
        "data": results,
    }
