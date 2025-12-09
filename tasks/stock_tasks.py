# price_app/tasks/stock_tasks.py (THIN CELERY WRAPPERS)
from celery import shared_task
from services.stock_services import fetch_stock_price_data, store_stock_price_data
import logging

logger = logging.getLogger(__name__)

@shared_task(name="tasks.stock_tasks.fetch_stock_price", bind=True, max_retries=3)
def fetch_stock_price(self, symbol, start_date=None, end_date=None):
    """Fetch stock price data via Celery"""
    try:
        return fetch_stock_price_data(symbol, start_date, end_date)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task(name="tasks.stock_tasks.store_stock_price", bind=True, max_retries=2)
def store_stock_price(self, price_data, collection_name):
    """Store stock price data via Celery"""
    try:
        from app.main import orm_app
        collection = orm_app.get_collection(collection_name)
        return store_stock_price_data(price_data, collection)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
