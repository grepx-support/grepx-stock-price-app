"""Example usage of ConfigLoader."""
from price_app.src.main.servers.config import ConfigLoader


def example_basic_usage():
    """Basic usage with ConfigLoader."""
    print("=== Basic Usage ===\n")
    
    loader = ConfigLoader()
    
    # Load app config
    app_cfg = loader.load_app_config()
    print(f"App: {app_cfg.app.name} v{app_cfg.app.version}")
    print(f"Database: {app_cfg.database.connection_string}")
    print(f"Celery Broker: {app_cfg.celery.broker_url}\n")
    
    # Load asset config
    asset_cfg = loader.load_asset_config()
    print(f"Stock symbols: {asset_cfg.asset_types.stocks.symbols}")
    print(f"Date range: {asset_cfg.start_date} to {asset_cfg.end_date}")
    print(f"SMA periods: {asset_cfg.indicators.SMA.periods}\n")
    
    # Load dagster config
    dagster_cfg = loader.load_dagster_config()
    print(f"Dagster module: {dagster_cfg.dagster.module_name}")
    print(f"Asset modules: {dagster_cfg.assets.modules}\n")
    
    loader.cleanup()


def example_load_all():
    """Load all configs at once."""
    print("=== Load All Configs ===\n")
    
    loader = ConfigLoader()
    app_cfg, asset_cfg, dagster_cfg = loader.load_all()
    
    print(f"App: {app_cfg.app.name}")
    print(f"Assets: {len(asset_cfg.asset_types.stocks.symbols)} stocks")
    print(f"Dagster: {dagster_cfg.dagster.module_name}\n")
    
    loader.cleanup()


def example_raw_config():
    """Load and override raw config."""
    print("=== Raw Config with Overrides ===\n")
    
    loader = ConfigLoader()
    
    # Load raw config
    raw_app = loader.load_raw("app")
    print(f"Original max_concurrent: {raw_app.worker.max_concurrent}")
    
    # Override values
    overrides = {"worker": {"max_concurrent": 10}}
    modified = loader.override_config(raw_app, overrides)
    print(f"Modified max_concurrent: {modified.worker.max_concurrent}\n")
    
    loader.cleanup()


def example_access_nested():
    """Access nested config values."""
    print("=== Access Nested Values ===\n")
    
    loader = ConfigLoader()
    app_cfg = loader.load_app_config()
    
    print(f"Celery timezone: {app_cfg.celery.timezone}")
    print(f"Worker pool: {app_cfg.worker.pool}")
    print(f"Task time limit: {app_cfg.task.time_limit}s")
    print(f"Task modules: {app_cfg.tasks.modules}\n")
    
    loader.cleanup()


if __name__ == "__main__":
    print("Configuration Loader Examples\n")
    print("=" * 60 + "\n")
    
    example_basic_usage()
    example_load_all()
    example_raw_config()
    example_access_nested()
