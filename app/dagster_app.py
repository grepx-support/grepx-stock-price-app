"""Dagster initialization for stock_data_app."""

import os

import yaml
from dagster import Definitions, fs_io_manager, FilesystemIOManager, in_process_executor

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "..", "config", "dagster_config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Import assets
from assets.stock_assets import close_price_download

# Get Dagster configuration
dagster_config = config.get("dagster", {})
storage_config = config.get("storage", {})

# Setup storage path - check environment variable first, then config
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

dagster_home = os.environ.get(
    "DAGSTER_HOME",
    os.path.join(PROJECT_ROOT, "dagster_home")  # fallback
)


# Get storage path from config or use default
storage_path_config = storage_config.get("sqlite_path", None)
if storage_path_config:
    # If config specifies a path, use it (expand user and env vars)
    storage_path = os.path.expanduser(os.path.expandvars(storage_path_config))
    # Replace ${DAGSTER_HOME} if present in the path
    if "${DAGSTER_HOME}" in storage_path_config:
        storage_path = storage_path.replace("${DAGSTER_HOME}", dagster_home)
else:
    # Default: use dagster_home/storage.db
    storage_path = os.path.join(dagster_home, "storage.db")

# Ensure directory exists
storage_dir = os.path.dirname(storage_path)
if storage_dir:
    os.makedirs(storage_dir, exist_ok=True)

# Create IOManager
# io_manager = FilesystemIOManager(base_dir=dagster_home)

# Create Definitions
defs = Definitions(
    assets=[close_price_download],
    resources={"io_manager": fs_io_manager},
    executor=in_process_executor,
)

