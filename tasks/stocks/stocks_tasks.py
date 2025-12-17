from celery import shared_task
from tasks.base_tasks import TaskFactory
from services.stock_services import (
    fetch_stock_price_data,
    store_stock_price_data
)
from services.indicator_services import compute_single_factor, store_single_factor
from services.naming import naming

# Create fetch task using factory
_fetch_func = TaskFactory.create_fetch_task(fetch_stock_price_data, "STOCKS")
fetch_stock_price = shared_task(
    name="tasks.stocks.stocks_tasks.fetch_stock_price",
    bind=True,
    max_retries=3
)(_fetch_func)

# Create store task using factory
_store_func = TaskFactory.create_store_task(
    store_stock_price_data,
    "STOCKS",
    # naming.get_price_collection_name
)
store_stock_price = shared_task(
    name="tasks.stocks.stocks_tasks.store_stock_price",
    bind=True,
    max_retries=2
)(_store_func)

# Create compute task using factory
_compute_func = TaskFactory.create_compute_task(compute_single_factor, "STOCKS")
compute = shared_task(
    name="tasks.stocks.stocks_tasks.compute",
    bind=True,
    max_retries=2
)(_compute_func)

# Create store indicator task using factory
_store_ind_func = TaskFactory.create_store_indicator_task(
    store_single_factor,
    "STOCKS",
    # naming.get_indicator_collection_name
)
store = shared_task(
    name="tasks.stocks.stocks_tasks.store",
    bind=True,
    max_retries=2
)(_store_ind_func)