from assets.base_assets import StockAssetFactory
from factors.config import cfg

config_prices_stocks = StockAssetFactory.create_prices_config_asset("stocks", "stocks")
config_indicators_stocks = StockAssetFactory.create_indicators_config_asset("stocks", "stocks")
globals()["config_prices_stocks"] = config_prices_stocks
globals()["config_indicators_stocks"] = config_indicators_stocks

# Create fetch asset
fetch_stocks = StockAssetFactory.create_fetch_asset(
    asset_type="stocks",
    task_name="tasks.stocks.stocks_tasks.fetch_stock_price",
    group_name="stocks"
)

# Create store asset
store_stocks = StockAssetFactory.create_store_asset(
    asset_type="stocks",
    task_name="tasks.stocks.stocks_tasks.store_stock_price",
    group_name="stocks"
)

# Create all indicator assets dynamically
for indicator_name in cfg.indicators.keys():
    indicator_asset = StockAssetFactory.create_indicator_asset(
        asset_type="stocks",
        indicator_name=indicator_name,
        group_name="stocks"
    )
    globals()[f"stocks_{indicator_name.lower()}_indicator"] = indicator_asset
    
# Get list of indicator names
indicator_names = list(cfg.indicators.keys())

# Create store_indicators asset
store_stocks_indicators = StockAssetFactory.create_store_indicators_asset(
    asset_type="stocks",
    task_name="tasks.stocks.stocks_tasks.store",  # the store indicator task
    group_name="stocks",
    indicator_names=indicator_names
)
globals()["store_stocks_indicators"] = store_stocks_indicators