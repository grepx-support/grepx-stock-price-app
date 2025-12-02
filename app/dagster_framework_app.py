"""
Integrate dagster_framework with price_app.
Auto-loads assets/ops from dagster_config.yaml only.
"""
from dagster_framework.main import create_app

from config.paths import DAGSTER_CONFIG, ROOT
import os

os.environ["PROJECT_ROOT"] = str(ROOT)

# Create Dagster Definitions using dynamic config path
defs = create_app(config_path=str(DAGSTER_CONFIG.parent))
