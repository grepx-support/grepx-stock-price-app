# dags/indices_pipeline.py
from datetime import datetime
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from apache_airflow_app.grepx_airflow.factories.dag_builder import DAGBuilder

# Generate the indices DAG
indices_dag = DAGBuilder.build_asset_type_dag(
    asset_type="indices",
    fetch_task="celery_app.tasks.indices.indices_tasks.fetch_indices_price",
    store_task="celery_app.tasks.indices.indices_tasks.store_indices_price",
    store_indicators_task="celery_app.tasks.indices.indices_tasks.store",
    start_date=datetime(2025, 1, 1),
)

# Make DAG available to Airflow
globals()['indices_pipeline'] = indices_dag


