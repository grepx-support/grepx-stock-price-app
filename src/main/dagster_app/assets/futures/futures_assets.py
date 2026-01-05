# dagster_app/assets/futures/futures_assets.py (bonus if you have this)
from dagster_app.assets.asset_factory_helper import create_asset_type

create_asset_type(
    asset_type="futures",
    group_name="futures",
    fetch_task="celery_app.tasks.futures.futures_tasks.fetch_futures_price",
    store_task="celery_app.tasks.futures.futures_tasks.store_futures_price",
    store_indicators_task="celery_app.tasks.futures.futures_tasks.store",
    globals_dict=globals()
)