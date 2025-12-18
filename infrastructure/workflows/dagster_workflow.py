"""Dagster workflow adapter."""

from typing import Dict, Any, List
from dagster import asset, AssetIn, get_dagster_logger
from application.ports.task_queue import ITaskQueue
import logging

logger = logging.getLogger(__name__)


class DagsterWorkflowAdapter:
    """Adapter for creating Dagster assets from use cases."""

    def __init__(self, task_queue: ITaskQueue):
        """
        Initialize with task queue.
        
        Args:
            task_queue: Task queue implementation
        """
        self.task_queue = task_queue

    def create_prices_config_asset(self, asset_type: str, group_name: str, symbols: List[str], start_date: str, end_date: str):
        """Create a configuration asset for prices."""
        @asset(
            name=f"config_prices_{asset_type}",
            group_name=group_name,
            description=f"Price fetching configuration for {asset_type}"
        )
        def config_prices_asset() -> Dict:
            return {
                "symbols": symbols,
                "start_date": start_date,
                "end_date": end_date,
            }
        return config_prices_asset

    def create_indicators_config_asset(self, asset_type: str, group_name: str, indicators_config: Dict):
        """Create a configuration asset for indicators."""
        @asset(
            name=f"config_indicators_{asset_type}",
            group_name=group_name,
            description=f"Indicator computation configuration for {asset_type}"
        )
        def config_indicators_asset() -> Dict:
            return indicators_config
        return config_indicators_asset

    def create_fetch_asset(self, asset_type: str, task_name: str, group_name: str):
        """Create a fetch asset."""
        @asset(
            name=f"fetch_{asset_type}",
            group_name=group_name,
            ins={"prices_config": AssetIn(f"config_prices_{asset_type}")},
            auto_materialize_policy=None,
        )
        def fetch_asset(prices_config: Dict) -> Dict[str, str]:
            dagster_logger = get_dagster_logger()
            task_ids = {}
            symbols = prices_config["symbols"]
            start_date = prices_config.get("start_date")
            end_date = prices_config.get("end_date")

            for symbol in symbols:
                task_id = self.task_queue.send_task(task_name, args=(symbol, start_date, end_date))
                task_ids[symbol] = task_id
                dagster_logger.info(f"[{asset_type.upper()}] Queued fetch: {symbol} -> {task_id}")

            return task_ids

        return fetch_asset

    def create_store_asset(self, asset_type: str, task_name: str, group_name: str):
        """Create a store asset."""
        @asset(
            name=f"store_{asset_type}",
            group_name=group_name,
            ins={"fetch_task_ids": AssetIn(f"fetch_{asset_type}")},
        )
        def store_asset(fetch_task_ids: Dict[str, str]) -> Dict:
            dagster_logger = get_dagster_logger()
            store_results = {}
            for symbol, task_id in fetch_task_ids.items():
                try:
                    price_data = self.task_queue.get_task_result(task_id, timeout=120)
                    if not price_data or price_data.get("status") != "success":
                        dagster_logger.warning(f"[{asset_type.upper()}] Fetch failed for {symbol}")
                        store_results[symbol] = None
                        continue
                    result_id = self.task_queue.send_task(task_name, args=(price_data, symbol, asset_type))
                    store_results[symbol] = result_id
                    dagster_logger.info(f"[{asset_type.upper()}] Queued store: {symbol} -> {result_id}")
                except Exception as e:
                    dagster_logger.error(f"[{asset_type.upper()}] Error storing {symbol}: {e}")
                    store_results[symbol] = None
            return store_results
        return store_asset

    def create_indicator_asset(self, asset_type: str, indicator_name: str, group_name: str, symbols: List[str]):
        """Create an indicator computation asset."""
        @asset(
            name=f"{asset_type}_{indicator_name.lower()}_indicator",
            group_name=group_name,
            ins={
                "fetch_task_ids": AssetIn(f"fetch_{asset_type}"),
                "indicators_config": AssetIn(f"config_indicators_{asset_type}")
            },
        )
        def indicator_asset(fetch_task_ids: Dict[str, str], indicators_config: Dict) -> List:
            dagster_logger = get_dagster_logger()
            results = []
            indicator_config = indicators_config.get(indicator_name, {})

            for symbol in symbols:
                task_id = fetch_task_ids.get(symbol)
                if not task_id:
                    continue
                try:
                    price_data = self.task_queue.get_task_result(task_id, timeout=120)
                    if price_data.get("status") == "success":
                        compute_task_name = "adapters.tasks.indicator_tasks.compute_indicator"
                        result_id = self.task_queue.send_task(
                            compute_task_name,
                            args=(symbol, indicator_name, price_data["records"], indicator_config),
                        )
                        results.append({
                            "symbol": symbol,
                            "factor": indicator_name,
                            "task_id": result_id
                        })
                except Exception as e:
                    dagster_logger.error(f"[{asset_type.upper()}] Error computing {indicator_name} for {symbol}: {e}")
            return results
        return indicator_asset

    def create_store_indicators_asset(self, asset_type: str, task_name: str, group_name: str, indicator_names: List[str]):
        """Create a store indicators asset."""
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
            dagster_logger = get_dagster_logger()
            store_results = []
            store_task_name = task_name  # Use provided task name

            for indicator_name in indicator_names:
                key = f"{indicator_name.lower()}_task_ids"
                compute_results: List[dict] = kwargs[key]

                for item in compute_results:
                    symbol = item["symbol"]
                    factor = item["factor"]
                    compute_task_id = item["task_id"]
                    try:
                        factor_data = self.task_queue.get_task_result(compute_task_id, timeout=180)
                        result_id = self.task_queue.send_task(
                            store_task_name,
                            args=(symbol, factor, factor_data, asset_type)
                        )
                        store_results.append({
                            "symbol": symbol,
                            "factor": factor,
                            "store_task_id": result_id
                        })
                        dagster_logger.info(f"[{asset_type.upper()}] Queued store indicator {factor} for {symbol} -> {result_id}")
                    except Exception as e:
                        dagster_logger.error(f"[{asset_type.upper()}] Error storing indicator {factor} for {symbol}: {e}")

            return store_results

        return store_indicators_asset

