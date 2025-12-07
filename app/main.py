# price_app/app/main.py

from config.paths import CELERY_CONFIG, DAGSTER_CONFIG, MONGO_CONFIG, ROOT
from .loader import AppLoader
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


if __name__ == "__main__":
    print("="*60)
    print("Price App Status")
    print("="*60)
    try:
        print(f"Celery: {len(celery_app.list_tasks())} tasks")
    except Exception as e:
        print(f"Celery: Error - {e}")
    
    try:
        print(f"MongoDB: {mongo_app.instance.db.name}")
    except Exception as e:
        print(f"MongoDB: Error - {e}")
    
    print(f"Dagster: Loaded")
    print("="*60)