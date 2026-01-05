
# airflow_app/operators/celery_result_operator.py
from airflow.operators.python import PythonOperator
import logging

logger = logging.getLogger(__name__)

class CeleryResultOperator(PythonOperator):
    """
    Retrieves result from a Celery task
    """
    def __init__(self, upstream_task_id: str = None, timeout: int = 300, **kwargs):
        self.upstream_task_id = upstream_task_id
        self.timeout = timeout
        super().__init__(**kwargs)

    def execute(self, context):
        from main import get_connection
        
        celery_app = get_connection("primary_celery").get_client()
        
        # Get task_id from upstream task
        task_id = context['task_instance'].xcom_pull(
            task_ids=self.upstream_task_id, 
            key='celery_task_id'
        )
        
        logger.info(f"Retrieving result for task: {task_id}")
        
        result = celery_app.AsyncResult(task_id).get(timeout=self.timeout)
        
        logger.info(f"Task result: {result}")
        context['task_instance'].xcom_push(key='celery_result', value=result)
        
        return result
