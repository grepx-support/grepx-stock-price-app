from dagster_app.assets.base_assets import StockAssetFactory
from servers.factors.config import cfg

config_prices_indices = StockAssetFactory.create_prices_config_asset("indices", "indices")
config_indicators_indices = StockAssetFactory.create_indicators_config_asset("indices", "indices")
globals()["config_prices_indices"] = config_prices_indices
globals()["config_indicators_indices"] = config_indicators_indices

# Create fetch asset
fetch_indices = StockAssetFactory.create_fetch_asset(
    asset_type="indices",
    task_name="celery_app.tasks.indices.indices_tasks.fetch_indices_price",
    group_name="indices"
)

# Create store asset
store_indices = StockAssetFactory.create_store_asset(
    asset_type="indices",
    task_name="celery_app.tasks.indices.indices_tasks.store_indices_price",
    group_name="indices"
)

# Create all indicator assets dynamically
for indicator_name in cfg.indicators.keys():
    indicator_asset = StockAssetFactory.create_indicator_asset(
        asset_type="indices",
        indicator_name=indicator_name,
        group_name="indices"
    )
    globals()[f"indices_{indicator_name.lower()}_indicator"] = indicator_asset
    
indicator_names = list(cfg.indicators.keys())

# Create store_indicators asset
store_indices_indicators = StockAssetFactory.create_store_indicators_asset(
    asset_type="indices",
    task_name="celery_app.tasks.indices.indices_tasks.store",  # the store indicator task
    group_name="indices",
    indicator_names=indicator_names
)
globals()["store_indices_indicators"] = store_indices_indicators