# price_app/app/main.py

from config.paths import CELERY_CONFIG, DAGSTER_CONFIG, MONGO_CONFIG, ROOT
from app.loader import AppLoader
import os

os.environ["PROJECT_ROOT"] = str(ROOT)

# Create loaders
celery_app = AppLoader(
    name="Celery",
    config_path=CELERY_CONFIG,
    factory=lambda cfg: __import__('celery_framework').create_app(cfg)
)

dagster_app = AppLoader(
    name="Dagster",
    config_path=None,
    factory=lambda: __import__('dagster_framework.main', fromlist=['create_app']).create_app(
        config_path=str(DAGSTER_CONFIG.parent)
    )
)

mongo_app = AppLoader(
    name="MongoDB",
    config_path=MONGO_CONFIG,
    factory=lambda cfg: __import__('mongo_connection', fromlist=['create_app']).create_app(cfg)
)

# Expose Celery app instance for CLI usage (celery -A app.main worker)
app = celery_app.instance.app

# Expose Dagster definitions for CLI usage (dagster dev -f app.main)
defs = dagster_app.instance