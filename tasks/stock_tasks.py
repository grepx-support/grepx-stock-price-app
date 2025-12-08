# price_app/tasks/stock_tasks.py (THIN CELERY WRAPPERS)

from celery_framework.tasks.decorators import task
from services.stock_services import fetch_stock_price_data, store_stock_price_data


@task(name="fetch_stock_price")
def fetch_stock_price(symbol: str):
    """Celery task: fetch price"""
    return fetch_stock_price_data(symbol)


@task(name="store_stock_price")
def store_stock_price(price_data: dict):
    """Celery task: store price"""
    # Lazy import to avoid circular dependency
    from app.main import mongo_app
    collection = mongo_app.connection.collection("stock_prices")
    return store_stock_price_data(price_data, collection)