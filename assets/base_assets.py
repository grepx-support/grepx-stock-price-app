# price_app/assets/base_assets.py
from dagster import asset, get_dagster_logger, AssetIn
from app.main import app as celery_app
from typing import Dict, List
from factors.config import cfg
from omegaconf import OmegaConf

class StockAssetFactory:
    @staticmethod
    def create_prices_config_asset(asset_type: str, group_name: str):
        @asset(
            name=f"config_prices_{asset_type}",
            group_name=group_name,
            description=f"Price fetching configuration for {asset_type}"
        )
        def config_prices_asset() -> Dict:
            return {
                "symbols": cfg.asset_types[asset_type].symbols,
                "start_date": cfg.start_date,
                "end_date": cfg.end_date,
            }
        return config_prices_asset

    @staticmethod
    def create_indicators_config_asset(asset_type: str, group_name: str):
        @asset(
            name=f"config_indicators_{asset_type}",
            group_name=group_name,
            description=f"Indicator computation configuration for {asset_type}"
        )
        def config_indicators_asset() -> Dict:
            return OmegaConf.to_container(cfg.indicators, resolve=True)
        return config_indicators_asset

    @staticmethod
    def create_fetch_asset(asset_type: str, task_name: str, group_name: str):
        @asset(
            name=f"fetch_{asset_type}",
            group_name=group_name,
            ins={"prices_config": AssetIn(f"config_prices_{asset_type}")},
            auto_materialize_policy=None,
        )
        def fetch_asset(prices_config: Dict) -> Dict[str, str]:
            logger = get_dagster_logger()
            task_ids = {}
            symbols = prices_config["symbols"]
            start_date = prices_config["start_date"]
            end_date = prices_config["end_date"]

            for symbol in symbols:
                result = celery_app.send_task(task_name, args=[symbol, start_date, end_date])
                task_ids[symbol] = result.id
                logger.info(f"[{asset_type.upper()}] Queued fetch: {symbol} -> {result.id}")

            return task_ids

        return fetch_asset

    @staticmethod
    def create_store_asset(asset_type: str, task_name: str, group_name: str):
        @asset(
            name=f"store_{asset_type}",
            group_name=group_name,
            ins={"fetch_task_ids": AssetIn(f"fetch_{asset_type}")},
        )
        def store_asset(fetch_task_ids: Dict[str, str]) -> Dict:
            logger = get_dagster_logger()
            store_results = {}
            for symbol, task_id in fetch_task_ids.items():
                try:
                    price_data = celery_app.AsyncResult(task_id).get(timeout=120)
                    if not price_data or price_data.get("status") != "success":
                        logger.warning(f"[{asset_type.upper()}] Fetch failed for {symbol}")
                        store_results[symbol] = None
                        continue
                    result = celery_app.send_task(task_name, args=[price_data, symbol])
                    store_results[symbol] = result.id
                    logger.info(f"[{asset_type.upper()}] Queued store: {symbol} -> {result.id}")
                except Exception as e:
                    logger.error(f"[{asset_type.upper()}] Error storing {symbol}: {e}")
                    store_results[symbol] = None
            return store_results
        return store_asset

    @staticmethod
    def create_indicator_asset(asset_type: str, indicator_name: str, group_name: str):
        @asset(
            name=f"{asset_type}_{indicator_name.lower()}_indicator",
            group_name=group_name,
            ins={
                "fetch_task_ids": AssetIn(f"fetch_{asset_type}"),
                "indicators_config": AssetIn(f"config_indicators_{asset_type}")
            },
        )
        def indicator_asset(fetch_task_ids: Dict[str, str], indicators_config: Dict) -> List:
            logger = get_dagster_logger()
            results = []
            symbols = cfg.asset_types[asset_type].symbols  # could also come from prices_config if you add it
            indicator_config = indicators_config.get(indicator_name, {})

            for symbol in symbols:
                task_id = fetch_task_ids.get(symbol)
                if not task_id:
                    continue
                try:
                    price_data = celery_app.AsyncResult(task_id).get(timeout=120)
                    if price_data.get("status") == "success":
                        result = celery_app.send_task(
                            f'tasks.{asset_type}.{asset_type}_tasks.compute',
                            args=[symbol, indicator_name, price_data["records"], indicator_config],
                        )
                        results.append({
                            "symbol": symbol,
                            "factor": indicator_name,
                            "task_id": result.id
                        })
                except Exception as e:
                    logger.error(f"[{asset_type.upper()}] Error computing {indicator_name} for {symbol}: {e}")
            return results
        return indicator_asset

    @staticmethod
    def create_store_indicators_asset(asset_type: str, task_name: str, group_name: str, indicator_names: List[str]):
        ins_dict = {
            f"{indicator_name.lower()}_task_ids": AssetIn(f"{asset_type}_{indicator_name.lower()}_indicator")
            for indicator_name in indicator_names
        }

        @asset(
            name=f"store_{asset_type}_indicators",
            group_name=group_name,
            ins=ins_dict,
            description=f"Store all computed indicators for {asset_type}",
        )
        def store_indicators_asset(**kwargs) -> List:
            logger = get_dagster_logger()
            store_results = []
            store_task_name = f"tasks.{asset_type}.{asset_type}_tasks.store"

            for indicator_name in indicator_names:
                key = f"{indicator_name.lower()}_task_ids"
                compute_results: List[dict] = kwargs[key]

                for item in compute_results:
                    symbol = item["symbol"]
                    factor = item["factor"]
                    compute_task_id = item["task_id"]
                    try:
                        factor_data = celery_app.AsyncResult(compute_task_id).get(timeout=180)
                        result = celery_app.send_task(
                            store_task_name,
                            args=[symbol, factor, factor_data]
                        )
                        store_results.append({
                            "symbol": symbol,
                            "factor": factor,
                            "store_task_id": result.id
                        })
                        logger.info(f"[{asset_type.upper()}] Queued store indicator {factor} for {symbol} -> {result.id}")
                    except Exception as e:
                        logger.error(f"[{asset_type.upper()}] Error storing indicator {factor} for {symbol}: {e}")

            return store_results

        return store_indicators_asset