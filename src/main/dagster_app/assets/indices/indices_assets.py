
# dagster_app/assets/indices/indices_assets.py
from dagster_app.assets.asset_factory_helper import create_asset_type

create_asset_type(
    asset_type="indices",
    group_name="indices",
    fetch_task="celery_app.tasks.indices.indices_tasks.fetch_indices_price",
    store_task="celery_app.tasks.indices.indices_tasks.store_indices_price",
    store_indicators_task="celery_app.tasks.indices.indices_tasks.store",
    globals_dict=globals()
)
