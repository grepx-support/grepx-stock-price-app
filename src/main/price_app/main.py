# price_app/app/main.py

from pathlib import Path
from omegaconf import OmegaConf
import os
import sys
import asyncio
import threading

# Setup paths
ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "resources"
CONFIG_FILE = CONFIG_DIR / "resources.yaml"
os.environ["PROJECT_ROOT"] = str(ROOT)

# Add ormlib to path (parent directory so 'src' imports work)
ormlib_path = ROOT.parent / "libs" / "py-orm-libs"
if str(ormlib_path) not in sys.path:
    sys.path.insert(0, str(ormlib_path))

# Load resources
config = OmegaConf.load(CONFIG_FILE)

# Initialize frameworks
from celery_framework import create_app as create_celery_app
from src.core import Session  # Must import after path setup
from dagster_framework.main import create_app as create_dagster_app

# Create apps
celery_app = create_celery_app(config)
app = celery_app.app  # Expose for celery CLI

# Create ORM connection (simple like basic_usage example)

_lock = threading.Lock()
orm_session = None

def get_orm_session():
    """Get or create ORM session (lazy initialization with async connection)"""
    global orm_session
    
    if orm_session is None:
        with _lock:
            if orm_session is None:  # Double-check locking
                orm_session = Session.from_connection_string(config.database.connection_string)
                asyncio.run(orm_session.__aenter__())
    
    return orm_session.backend.client

class ORMApp:
    def get_database(self, db_name: str):
        """Get a specific database by name"""
        client = get_orm_session()
        return client[db_name]

    def get_collection(self, db_name: str, collection_name: str):
        """Convenience: directly get collection in specific DB"""
        return self.get_database(db_name)[collection_name]

orm_app = ORMApp()

defs = create_dagster_app(config_path=str(CONFIG_DIR))  # Dagster uses its own resources file
