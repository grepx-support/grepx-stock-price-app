"""Celery task for downloading stock close prices."""

from celery_framework.tasks.decorators import task
import time
import random

@task(name="tasks.download_close_price")
def download_close_price(symbol: str):

    """
    Download close price for a stock symbol.
    This would normally call an API, but we'll simulate it.
    """

    print(f"Downloading close price for {symbol}...")
    time.sleep(2)  # Simulate API call
    
    # Simulate downloaded data
    close_price = round(random.uniform(100, 500), 2)
    
    result = {
        "symbol": symbol,
        "close_price": close_price,
        "status": "success"
    }
    
    print(f"Downloaded: {symbol} = ${close_price}")
    return result

