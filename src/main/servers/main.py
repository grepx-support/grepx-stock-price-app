"""Main application entry point."""
import sys
import os
from pathlib import Path
from omegaconf import OmegaConf

from servers import ConnectionManager

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
# Initialize connection manager
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


# Expose Celery app for celery CLI (loaded at import time)
app = get_celery_app()

# Expose Dagster defs for dagster CLI (lazy-loaded to avoid loading when celery starts)
# Dagster CLI expects 'defs' as a module-level variable, but we don't want to initialize
# it when celery/flower imports this module. So we use a lazy loader.
class _LazyDagsterDefs:
    """Lazy loader for dagster definitions - only loads when accessed."""
    _defs = None
    _error = None
    
    def _load(self):
        """Load dagster definitions if not already loaded."""
        if self._defs is None and self._error is None:
            try:
                self._defs = get_dagster_defs()
            except Exception as e:
                self._error = e
                raise
    
    def __call__(self):
        """Allow calling as function."""
        self._load()
        return self._defs
    
    def __getattr__(self, name):
        """Allow attribute access on the definitions object."""
        self._load()
        return getattr(self._defs, name)
    
    def __getitem__(self, key):
        """Allow dictionary-like access."""
        self._load()
        return self._defs[key]
    
    def __iter__(self):
        """Allow iteration."""
        self._load()
        return iter(self._defs)
    
    def __repr__(self):
        """String representation."""
        if self._defs is not None:
            return repr(self._defs)
        return "<LazyDagsterDefs (not loaded)>"

# Dagster CLI expects 'defs' as a module-level variable
# This lazy wrapper only initializes dagster when actually accessed by dagster CLI
defs = _LazyDagsterDefs()


if __name__ == "__main__":
    print("Initializing connections...")
    print(f"✓ Database: {get_database()}")
    print(f"✓ Celery: {app}")
    print(f"✓ Dagster: {defs}")
    print("\nAll connections initialized!")
