from celery import shared_task
from celery_app.tasks.base_tasks import TaskFactory
from database_app.services.stock_services import fetch_stock_price_data, store_stock_price_data
from database_app.services.indicator_services import compute_single_factor, store_single_factor
from database_app.services.naming import naming

def create_market_tasks(market: str, fetch_func=fetch_stock_price_data):
    """
    Generic function to create Celery tasks for a given market.
    """
    tasks = {}

    # Fetch task
    _fetch_func = TaskFactory.create_fetch_task(fetch_func, market)
    tasks[f"fetch_{market.lower()}_price"] = shared_task(
        name=f"celery_app.tasks.{market.lower()}.{market.lower()}_tasks.fetch_{market.lower()}_price",
        bind=True,
        max_retries=3
    )(_fetch_func)

    # Store price task
    _store_func = TaskFactory.create_store_task(store_stock_price_data, market)
    tasks[f"store_{market.lower()}_price"] = shared_task(
        name=f"celery_app.tasks.{market.lower()}.{market.lower()}_tasks.store_{market.lower()}_price",
        bind=True,
        max_retries=2
    )(_store_func)

    # Compute task
    _compute_func = TaskFactory.create_compute_task(compute_single_factor, market)
    tasks[f"compute_{market.lower()}"] = shared_task(
        name=f"celery_app.tasks.{market.lower()}.{market.lower()}_tasks.compute",
        bind=True,
        max_retries=2
    )(_compute_func)

    # Store indicator task
    _store_ind_func = TaskFactory.create_store_indicator_task(store_single_factor, market)
    tasks[f"store_{market.lower()}_indicator"] = shared_task(
        name=f"celery_app.tasks.{market.lower()}.{market.lower()}_tasks.store",
        bind=True,
        max_retries=2
    )(_store_ind_func)

    return tasks