
# airflow_app/factories/base_dag_factory.py
    
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from typing import Dict, List, Callable
from servers.factors.config import cfg
from omegaconf import OmegaConf
import logging

logger = logging.getLogger(__name__)

class DAGFactory:
    """
    Factory to create DAGs similar to Dagster's AssetFactory
    """
    
    @staticmethod
    def create_config_prices_task(asset_type: str, dag: DAG):
        """Create task that returns prices configuration"""
        def _get_prices_config():
            return {
                "symbols": cfg.asset_types[asset_type].symbols,
                "start_date": cfg.start_date,
                "end_date": cfg.end_date,
            }
        
        return PythonOperator(
            task_id=f"config_prices_{asset_type}",
            python_callable=_get_prices_config,
            dag=dag,
            do_xcom_push=True,
        )

    @staticmethod
    def create_config_indicators_task(asset_type: str, dag: DAG):
        """Create task that returns indicators configuration"""
        def _get_indicators_config():
            return OmegaConf.to_container(cfg.indicators, resolve=True)
        
        return PythonOperator(
            task_id=f"config_indicators_{asset_type}",
            python_callable=_get_indicators_config,
            dag=dag,
            do_xcom_push=True,
        )

    @staticmethod
    def create_fetch_task(asset_type: str, task_name: str, dag: DAG):
        """Create task to fetch prices via Celery"""
        def _fetch_prices(**context):
            from main import get_connection
            
            # Get config from upstream task
            prices_config = context['task_instance'].xcom_pull(
                task_ids=f"config_prices_{asset_type}",
                key='return_value'
            )
            
            celery_app = get_connection("primary_celery").get_client()
            task_ids = {}
            symbols = prices_config["symbols"]
            start_date = prices_config["start_date"]
            end_date = prices_config["end_date"]
            
            for symbol in symbols:
                result = celery_app.send_task(task_name, args=[symbol, start_date, end_date])
                task_ids[symbol] = result.id
                logger.info(f"[{asset_type.upper()}] Queued fetch: {symbol} -> {result.id}")
            
            return task_ids
        
        return PythonOperator(
            task_id=f"fetch_{asset_type}",
            python_callable=_fetch_prices,
            dag=dag,
            do_xcom_push=True,
        )

    @staticmethod
    def create_store_task(asset_type: str, task_name: str, dag: DAG):
        """Create task to store fetched prices via Celery"""
        def _store_prices(**context):
            from main import get_connection
            
            fetch_task_ids = context['task_instance'].xcom_pull(
                task_ids=f"fetch_{asset_type}",
                key='return_value'
            )
            
            celery_app = get_connection("primary_celery").get_client()
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
        
        return PythonOperator(
            task_id=f"store_{asset_type}",
            python_callable=_store_prices,
            dag=dag,
            do_xcom_push=True,
        )

    @staticmethod
    def create_indicator_task(asset_type: str, indicator_name: str, dag: DAG):
        """Create task to compute indicators via Celery"""
        def _compute_indicator(**context):
            from main import get_connection
            
            fetch_task_ids = context['task_instance'].xcom_pull(
                task_ids=f"fetch_{asset_type}",
                key='return_value'
            )
            
            indicators_config = context['task_instance'].xcom_pull(
                task_ids=f"config_indicators_{asset_type}",
                key='return_value'
            )
            
            celery_app = get_connection("primary_celery").get_client()
            results = []
            symbols = cfg.asset_types[asset_type].symbols
            indicator_config = indicators_config.get(indicator_name, {})
            
            for symbol in symbols:
                task_id = fetch_task_ids.get(symbol)
                if not task_id:
                    continue
                
                try:
                    price_data = celery_app.AsyncResult(task_id).get(timeout=120)
                    if price_data.get("status") == "success":
                        result = celery_app.send_task(
                            f'celery_app.tasks.{asset_type}.{asset_type}_tasks.compute',
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
        
        return PythonOperator(
            task_id=f"{asset_type}_{indicator_name.lower()}_indicator",
            python_callable=_compute_indicator,
            dag=dag,
            do_xcom_push=True,
        )

    @staticmethod
    def create_store_indicators_task(asset_type: str, task_name: str, dag: DAG, indicator_names: List[str]):
        """Create task to store all computed indicators via Celery"""
        def _store_indicators(**context):
            from main import get_connection
            
            celery_app = get_connection("primary_celery").get_client()
            store_results = []
            store_task_name = f"celery_app.tasks.{asset_type}.{asset_type}_tasks.store"
            
            for indicator_name in indicator_names:
                compute_results = context['task_instance'].xcom_pull(
                    task_ids=f"{asset_type}_{indicator_name.lower()}_indicator",
                    key='return_value'
                )
                
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
        
        return PythonOperator(
            task_id=f"store_{asset_type}_indicators",
            python_callable=_store_indicators,
            dag=dag,
            do_xcom_push=True,
        )
