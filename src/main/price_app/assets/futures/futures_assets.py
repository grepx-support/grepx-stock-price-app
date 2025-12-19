from assets.base_assets import StockAssetFactory
from factors.config import cfg

config_prices_futures = StockAssetFactory.create_prices_config_asset("futures", "futures")
config_indicators_futures = StockAssetFactory.create_indicators_config_asset("futures", "futures")
globals()["config_prices_futures"] = config_prices_futures
globals()["config_indicators_futures"] = config_indicators_futures

# Create fetch asset
fetch_futures = StockAssetFactory.create_fetch_asset(
    asset_type="futures",
    task_name="tasks.futures.futures_tasks.fetch_futures_price",
    group_name="futures"
)

# Create store asset
store_futures = StockAssetFactory.create_store_asset(
    asset_type="futures",
    task_name="tasks.futures.futures_tasks.store_futures_price",
    group_name="futures"
)

# Create all indicator assets dynamically
for indicator_name in cfg.indicators.keys():
    indicator_asset = StockAssetFactory.create_indicator_asset(
        asset_type="futures",
        indicator_name=indicator_name,
        group_name="futures"
    )
    globals()[f"futures_{indicator_name.lower()}_indicator"] = indicator_asset
    
indicator_names = list(cfg.indicators.keys())

# Create store_indicators asset
store_futures_indicators = StockAssetFactory.create_store_indicators_asset(
    asset_type="futures",
    task_name="tasks.futures.futures_tasks.store",  # the store indicator task
    group_name="futures",
    indicator_names=indicator_names
)
globals()["store_futures_indicators"] = store_futures_indicators