"""Main application entry point."""
import os
import sys
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

config = OmegaConf.load(CONFIG_FILE)
connections = ConnectionManager(config, CONFIG_DIR)

# Convenience accessors
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


# Expose for direct access
app = get_celery_app  # For celery CLI: celery -A price_app.main worker
defs = get_dagster_defs  # For dagster CLI

if __name__ == "__main__":
    print("Initializing connections...")
    print(f"✓ Database: {get_database()}")
    print(f"✓ Celery: {get_celery_app()}")
    print(f"✓ Dagster: {get_dagster_defs()}")
    print("\nAll connections initialized!")
