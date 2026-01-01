# airflow_app/operators/celery_operator.py
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class CeleryTaskOperator(PythonOperator):
    """
    Custom operator to submit tasks to Celery and retrieve results
    """
    def __init__(self, task_name: str, task_args: List = None, timeout: int = 300, **kwargs):
        self.task_name = task_name
        self.task_args = task_args or []
        self.timeout = timeout
        super().__init__(**kwargs)

    def execute(self, context):
        from main import get_connection
        
        celery_app = get_connection("primary_celery").get_client()
        result = celery_app.send_task(self.task_name, args=self.task_args)
        
        logger.info(f"Submitted task {self.task_name} with ID: {result.id}")
        
        # Store task_id in XCom for downstream tasks
        context['task_instance'].xcom_push(key='celery_task_id', value=result.id)
        
        return result.id

