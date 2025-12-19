"""Main application entry point."""

import sys
import os
from pathlib import Path
from omegaconf import OmegaConf

from price_app.src.main.price_app.connections.connection_manager import ConnectionManager

# Setup paths
ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "resources"
CONFIG_FILE = CONFIG_DIR / "app.yaml"
os.environ["PROJECT_ROOT"] = str(ROOT)

# Add ormlib to path
ormlib_path = ROOT.parent / "libs" / "py-orm-libs"
if str(ormlib_path) not in sys.path:
    sys.path.insert(0, str(ormlib_path))

# Load config
config = OmegaConf.load(CONFIG_FILE)
connections = ConnectionManager(config, CONFIG_DIR)


# Get connections (lazy loaded)
def get_database(db_name: str = None):
    """Get database or specific database."""
    db = connections.get_database()
    return db.get_database(db_name) if db_name else db.get_client()


def get_collection(db_name: str, collection_name: str):
    """Get specific collection."""
    return connections.get_database().get_collection(db_name, collection_name)


def get_celery_app():
    """Get Celery app."""
    return connections.get_celery().get_client()


def get_dagster_defs():
    """Get Dagster definitions."""
    return connections.get_dagster().get_definitions()


# Expose Celery app for celery CLI
app = get_celery_app()

# Expose Dagster defs for dagster CLI
defs = get_dagster_defs()


if __name__ == "__main__":
    print("Initializing connections...")
    print(f"✓ Database: {get_database()}")
    print(f"✓ Celery: {app}")
    print(f"✓ Dagster: {defs}")
    print("\nAll connections initialized!")
