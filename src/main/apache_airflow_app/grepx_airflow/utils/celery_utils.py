# airflow_app/utils/celery_utils.py
"""
Utility functions for Celery integration with Airflow
"""
import logging
from typing import Any, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def submit_celery_task(celery_app, task_name: str, args: List, **kwargs) -> str:
    """
    Submit a task to Celery with retry logic
    
    Args:
        celery_app: Celery application instance
        task_name: Full task name (e.g., 'celery_app.tasks.stocks.stocks_tasks.fetch_stocks_price')
        args: Arguments to pass to the task
    
    Returns:
        Task ID as string
    """
    try:
        result = celery_app.send_task(task_name, args=args, **kwargs)
        logger.info(f"Submitted Celery task {task_name} with ID: {result.id}")
        return result.id
    except Exception as e:
        logger.error(f"Failed to submit Celery task {task_name}: {e}")
        raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def get_celery_result(celery_app, task_id: str, timeout: int = 300) -> Any:
    """
    Retrieve result from a Celery task with retry logic
    
    Args:
        celery_app: Celery application instance
        task_id: Celery task ID
        timeout: Timeout in seconds
    
    Returns:
        Task result
    """
    try:
        result = celery_app.AsyncResult(task_id).get(timeout=timeout)
        logger.info(f"Retrieved result for task {task_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve result for task {task_id}: {e}")
        raise

def check_celery_result_status(celery_app, task_id: str) -> Dict[str, Any]:
    """
    Check the status of a Celery task without blocking
    
    Returns:
        Dictionary with status and info
    """
    async_result = celery_app.AsyncResult(task_id)
    return {
        'task_id': task_id,
        'state': async_result.state,
        'info': async_result.info,
        'successful': async_result.successful(),
        'failed': async_result.failed(),
    }


