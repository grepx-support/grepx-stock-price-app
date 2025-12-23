from dagster_app.assets.asset_factory_helper import create_asset_type

create_asset_type(
    asset_type="stocks",
    group_name="stocks",
    fetch_task="celery_app.tasks.stocks.stocks_tasks.fetch_stocks_price",
    store_task="celery_app.tasks.stocks.stocks_tasks.store_stocks_price",
    store_indicators_task="celery_app.tasks.stocks.stocks_tasks.store",
    globals_dict=globals()
)
