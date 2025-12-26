
# airflow_app/factories/dag_builder.py

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from typing import List
from servers.factors.config import cfg
from apache_airflow_app.grepx_airflow.factories.base_dag_factory import DAGFactory
import logging

logger = logging.getLogger(__name__)

class DAGBuilder:
    """
    Helper class to build complete DAGs for asset types
    Similar to asset_factory_helper.py in Dagster
    """
    
    @staticmethod
    def build_asset_type_dag(
        asset_type: str,
        fetch_task: str,
        store_task: str,
        store_indicators_task: str,
        start_date: datetime = None,
        schedule_interval: str = None,
    ) -> DAG:
        """
        Build a complete DAG for an asset type with all related tasks
        """
        if start_date is None:
            start_date = datetime(2025, 1, 1)
        
        default_args = {
            'owner': 'airflow',
            'retries': 2,
            'retry_delay': timedelta(minutes=5),
            'execution_timeout': timedelta(hours=2),
        }
        
        dag = DAG(
            dag_id=f"{asset_type}_pipeline",
            default_args=default_args,
            description=f"Pipeline for {asset_type} price and indicator computation",
            schedule_interval=schedule_interval or '@daily',
            start_date=start_date,
            catchup=False,
            tags=['celery', asset_type],
        )
        
        # Create config tasks
        config_prices_task = DAGFactory.create_config_prices_task(asset_type, dag)
        config_indicators_task = DAGFactory.create_config_indicators_task(asset_type, dag)
        
        # Create fetch task
        fetch_task_obj = DAGFactory.create_fetch_task(asset_type, fetch_task, dag)
        
        # Create store task
        store_task_obj = DAGFactory.create_store_task(asset_type, store_task, dag)
        
        # Create indicator tasks
        indicator_tasks = {}
        for indicator_name in cfg.indicators.keys():
            task = DAGFactory.create_indicator_task(asset_type, indicator_name, dag)
            indicator_tasks[indicator_name] = task
        
        # Create store indicators task
        store_indicators_task_obj = DAGFactory.create_store_indicators_task(
            asset_type,
            store_indicators_task,
            dag,
            list(cfg.indicators.keys())
        )
        
        # Set dependencies
        config_prices_task >> fetch_task_obj >> store_task_obj
        config_indicators_task >> [indicator_tasks[ind] for ind in cfg.indicators.keys()]
        [indicator_tasks[ind] for ind in cfg.indicators.keys()] >> store_indicators_task_obj
        
        return dag