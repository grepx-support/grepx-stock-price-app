# price_app/app/main.py

from pathlib import Path
from omegaconf import OmegaConf
import os
import sys
import asyncio

# Setup paths
ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
os.environ["PROJECT_ROOT"] = str(ROOT)

# Add ormlib to path (parent directory so 'src' imports work)
ormlib_path = ROOT.parent / "libs" / "py-orm-libs"
if str(ormlib_path) not in sys.path:
    sys.path.insert(0, str(ormlib_path))

# Load config
config = OmegaConf.load(CONFIG_FILE)

# Initialize frameworks
from celery_framework import create_app as create_celery_app
from src.core import Session  # Must import after path setup
from dagster_framework.main import create_app as create_dagster_app

# Create apps
celery_app = create_celery_app(config)
app = celery_app.app  # Expose for celery CLI

# Create ORM connection (simple like basic_usage example)
orm_session = Session.from_connection_string(config.database.connection_string)
asyncio.run(orm_session.__aenter__())  # Connect
orm_app = type('obj', (), {'get_collection': lambda name: orm_session.backend.database[name]})()

defs = create_dagster_app(config_path=str(CONFIG_DIR))  # Dagster uses its own config file
