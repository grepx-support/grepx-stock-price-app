from celery_app.tasks.tasks_factory_helper import create_market_tasks
stocks_tasks = create_market_tasks("STOCKS")
