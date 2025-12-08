# price_app/tasks/stock_tasks.py (THIN CELERY WRAPPERS)

from app.main import celery_app, mongo_app
from services.stock_service import fetch_stock_price_data, store_stock_price_data


@celery_app.instance.app.task(name="fetch_stock_price")
def fetch_stock_price(symbol: str):
    """Celery task: fetch price"""
    return fetch_stock_price_data(symbol)


@celery_app.instance.app.task(name="store_stock_price")
def store_stock_price(price_data: dict):
    """Celery task: store price"""
    collection = mongo_app.instance.collection("stock_prices")
    return store_stock_price_data(price_data, collection)