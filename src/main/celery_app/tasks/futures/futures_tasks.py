from celery_app.tasks.tasks_factory_helper import create_market_tasks
futures_tasks = create_market_tasks("FUTURES")
