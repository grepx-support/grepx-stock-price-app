# airflow_app/operators/__init__.py
from grepx_airflow.operators.celery_operator import CeleryTaskOperator
from grepx_airflow.operators.celery_result_operator import CeleryResultOperator

__all__ = [
    'CeleryTaskOperator',
    'CeleryResultOperator',
]


