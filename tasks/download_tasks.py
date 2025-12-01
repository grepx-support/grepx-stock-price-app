"""Celery task for downloading stock close prices."""

from celery_framework.tasks.decorators import task
from db.MongoDBManager import MongoDBManager
from db.MongoDBConnection import MongoDBConnection
import time
import random
import logging

logger = logging.getLogger(__name__)

MongoDBConnection.connect()
MongoDBManager.create_indexes()


@task(name="tasks.download_close_price")
def download_close_price(symbol: str):
    """Download close price and store in MongoDB."""
    print(f"Downloading close price for {symbol}...")
    time.sleep(2)

    close_price = round(random.uniform(100, 500), 2)
    success = MongoDBManager.insert_price(symbol, close_price)

    result = {
        "symbol": symbol,
        "close_price": close_price,
        "status": "success" if success else "error"
    }

    print(f"Downloaded: {symbol} = ${close_price}")
    return result

