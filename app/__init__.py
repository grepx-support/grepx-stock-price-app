# price_app/app/__init__.py

from config.paths import CELERY_CONFIG, DAGSTER_CONFIG, MONGO_CONFIG, ROOT
from .loader import AppLoader
import os

os.environ["PROJECT_ROOT"] = str(ROOT)

# Celery loader
celery_app = AppLoader(
    name="Celery",
    config_path=CELERY_CONFIG,
    factory=lambda cfg: __import__('celery_framework').create_app(cfg)
)

# Dagster loader
dagster_app = AppLoader(
    name="Dagster",
    config_path=None,
    factory=lambda: __import__('dagster_framework.main', fromlist=['create_app']).create_app(
        config_path=str(DAGSTER_CONFIG.parent)
    )
)

# MongoDB loader
mongo_app = AppLoader(
    name="MongoDB",
    config_path=MONGO_CONFIG,
    factory=lambda cfg: __import__('mongo_connection').create_app(cfg)
)

# Shortcuts
celery = celery_app.instance.app
dagster_defs = dagster_app.instance
db = mongo_app.instance.db
collection = mongo_app.instance.collection

__all__ = [
    'celery_app',
    'celery',
    'dagster_app',
    'dagster_defs',
    'mongo_app',
    'db',
    'collection',
]
