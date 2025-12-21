"""Application initialization - generic, no specific connection knowledge."""

import sys
from pathlib import Path

import database_app
import celery_app
import dagster_app

from servers.config import ConfigLoader
from servers.connections import ConnectionManager
from servers.app.connection_config import ConnectionConfig

ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT / "resources"

ormlib_path = ROOT.parent / "libs" / "py-orm-libs"
if str(ormlib_path) not in sys.path:
    sys.path.insert(0, str(ormlib_path))

loader = ConfigLoader(CONFIG_DIR)
config = loader.load_all()
connections = ConnectionManager(config, CONFIG_DIR)
conn_config = ConnectionConfig.from_config(config)


def get_connection(conn_id: str):
    """Get any connection by ID."""
    return connections.get(conn_id)
