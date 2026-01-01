# dags/stocks_pipeline.py
from datetime import datetime
import sys
import os

# Add project root to sys.path (robust way)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from apache_airflow_app.grepx_airflow.factories.dag_builder import DAGBuilder
# Generate the stocks DAG
stocks_dag = DAGBuilder.build_asset_type_dag(
    asset_type="stocks",
    fetch_task="celery_app.tasks.stocks.stocks_tasks.fetch_stocks_price",
    store_task="celery_app.tasks.stocks.stocks_tasks.store_stocks_price",
    store_indicators_task="celery_app.tasks.stocks.stocks_tasks.store",
    start_date=datetime(2025, 1, 1),
)

# Make DAG available to Airflow
globals()['stocks_pipeline'] = stocks_dag


