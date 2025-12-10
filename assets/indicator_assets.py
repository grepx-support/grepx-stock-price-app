# price_app/assets/indicator_assets.py
from dagster import asset, AssetIn, get_dagster_logger
from app.main import app as celery_app
from omegaconf import OmegaConf

cfg = OmegaConf.load("config/config.yaml")

@asset(group_name="indicators")
def indicator_config():
    return {
        "symbols": list(cfg.symbols),
        "factors": list(cfg.indicators.keys())
    }

def _create_indicator_asset(factor_name: str):
    @asset(
        name=f"{factor_name.lower()}_indicator",
        description=f"Compute {factor_name} for all symbols",
        group_name="indicators",
        ins={"fetch_stock_prices": AssetIn("fetch_stock_prices"), "indicator_config": AssetIn("indicator_config")}
    )
    def indicator_asset(fetch_stock_prices, indicator_config):
        logger = get_dagster_logger()
        results = []
        
        for symbol, fetch_task_id in fetch_stock_prices.items():
            try:
                price_data = celery_app.AsyncResult(fetch_task_id).get(timeout=180)
                if price_data.get("status") == "success":
                    result = celery_app.send_task(
                        "tasks.indicator_tasks.compute",
                        args=[symbol, factor_name, price_data["records"]]
                    )
                    results.append({"symbol": symbol, "factor": factor_name, "task_id": result.id})
            except Exception as e:
                logger.error(f"Failed to queue {factor_name} for {symbol}: {e}")
        
        return results
    
    return indicator_asset

# Dynamically create indicator assets
_indicator_names = list(cfg.indicators.keys())
for factor_name in _indicator_names:
    globals()[f"{factor_name.lower()}_indicator"] = _create_indicator_asset(factor_name)

# Dynamic store_indicators
def _create_store_indicators():
    ins_dict = {f"{name.lower()}_indicator": AssetIn(f"{name.lower()}_indicator") for name in _indicator_names}
    ins_dict["indicator_config"] = AssetIn("indicator_config")
    
    @asset(group_name="indicators", ins=ins_dict)
    def store_indicators(indicator_config, **kwargs):
        logger = get_dagster_logger()
        results = []
        
        for factor_name, indicator_list in {k: v for k, v in kwargs.items() if k != "indicator_config"}.items():
            for indicator_data in (indicator_list if isinstance(indicator_list, list) else [indicator_list]):
                symbol, factor, task_id = indicator_data["symbol"], indicator_data["factor"], indicator_data["task_id"]
                
                try:
                    factor_data = celery_app.AsyncResult(task_id).get(timeout=600)
                    if factor_data:
                        result = celery_app.send_task("tasks.indicator_tasks.store", args=[symbol, factor, factor_data])
                        results.append({"symbol": symbol, "factor": factor, "task_id": result.id, "status": "storing"})
                        logger.info(f"Queued storage for {symbol}_{factor}: {result.id}")
                except Exception as e:
                    logger.error(f"Failed to queue storage for {symbol}_{factor}: {e}")
                    results.append({"symbol": symbol, "factor": factor, "status": "failed", "error": str(e)})
        
        return results
    
    return store_indicators

store_indicators = _create_store_indicators()