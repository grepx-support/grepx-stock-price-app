# price_app/app/main.py

from pathlib import Path
from omegaconf import OmegaConf
import os

# Setup paths
ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

os.environ["PROJECT_ROOT"] = str(ROOT)

# Load config
config = OmegaConf.load(CONFIG_FILE)

# Initialize frameworks
from celery_framework import create_app as create_celery_app
from mongo_connection import create_app as create_mongo_app
from dagster_framework.main import create_app as create_dagster_app

# Create apps
celery_app = create_celery_app(config)
app = celery_app.app  # Expose for celery CLI

mongo_app = create_mongo_app(OmegaConf.create({"mongodb": config.mongodb}))

defs = create_dagster_app(config_path=str(CONFIG_DIR))  # Dagster uses its own config file
