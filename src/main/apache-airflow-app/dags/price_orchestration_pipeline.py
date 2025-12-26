from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from tasks import stocks, indices, futures

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "price_orchestration_pipeline_v2",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args
) as dag:

    for name, mod in {
        "stocks": stocks,
        "indices": indices,
        "futures": futures
    }.items():

        PythonOperator(task_id=f"{name}_load", python_callable=mod.load_config) \
        >> PythonOperator(task_id=f"{name}_fetch", python_callable=mod.fetch_prices) \
        >> PythonOperator(task_id=f"{name}_compute", python_callable=mod.compute_indicators) \
        >> PythonOperator(task_id=f"{name}_report", python_callable=mod.generate_report)
