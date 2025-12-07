# price_app/config/paths.py

from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_DIR = Path(__file__).parent

CELERY_CONFIG = CONFIG_DIR / "celery_config.yaml"
DAGSTER_CONFIG = CONFIG_DIR / "dagster_config.yaml"
MONGO_CONFIG = CONFIG_DIR / "database_config.yaml"