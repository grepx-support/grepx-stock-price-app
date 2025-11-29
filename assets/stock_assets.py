"""Dagster asset for close price download orchestration."""

from dagster import asset
from tasks.download_tasks import download_close_price

@asset(group_name="stock_data")
def close_price_download():
    """
    Dagster asset that triggers Celery task to download close prices.
    """
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    results = []
    for symbol in symbols:
        # Trigger Celery task asynchronously
        task = download_close_price.delay(symbol)
        
        # Wait for result (or you can store task_id and check later)
        result = task.get(timeout=10)
        results.append(result)
    
    return {
        "downloaded": len(results),
        "data": results
    }

