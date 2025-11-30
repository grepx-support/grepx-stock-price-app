"""Celery initialization for stock_data_app."""

import os
import yaml
from celery import Celery

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "config", "celery_config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Get Celery configuration
celery_config = config.get("celery", {})
app_config = config.get("app", {})

# Initialize Celery app
app = Celery(
    app_config.get("name", "stock_data_app"),
    broker=celery_config.get("broker_url", "redis://localhost:6379/0"),
    backend=celery_config.get("result_backend", "redis://localhost:6379/1"),
)

# Configure Celery app
app.conf.update(
    task_serializer=celery_config.get("task_serializer", "json"),
    result_serializer=celery_config.get("result_serializer", "json"),
    accept_content=celery_config.get("accept_content", ["json"]),
    timezone=celery_config.get("timezone", "Asia/Kolkata"),
    enable_utc=celery_config.get("enable_utc", True),
    task_track_started=config.get("task", {}).get("track_started", True),
    task_time_limit=config.get("task", {}).get("time_limit", 1800),
    task_soft_time_limit=config.get("task", {}).get("soft_time_limit", 1500),
    result_expires=config.get("task", {}).get("result_expires", 3600),
    worker_prefetch_multiplier=config.get("worker", {}).get("prefetch_multiplier", 1),
    worker_max_tasks_per_child=config.get("worker", {}).get("max_tasks_per_child", 50),
)

# Auto-discover tasks
# Add current directory to Python path to ensure tasks can be imported
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

app.autodiscover_tasks(["tasks"])

