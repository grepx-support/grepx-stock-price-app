"""Quick test script for config loaders."""

import sys
from pathlib import Path

from price_app.src.main.price_app.config import AppConfigLoader, AssetConfigLoader, DagsterConfigLoader

# Add src/main to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_app_config():
    print("Testing AppConfigLoader...")
    loader = AppConfigLoader()
    
    assert loader.config.app.name == "price_app"
    assert loader.celery_config.broker_url
    assert len(loader.task_modules) > 0
    
    print(f"  ✓ App name: {loader.config.app.name}")
    print(f"  ✓ Celery broker: {loader.celery_config.broker_url}")
    print(f"  ✓ Task modules: {len(loader.task_modules)}")
    print()


def test_asset_config():
    print("Testing AssetConfigLoader...")
    loader = AssetConfigLoader()
    
    assert len(loader.stock_symbols) > 0
    assert len(loader.all_symbols) > 0
    assert loader.indicators.SMA.periods
    
    print(f"  ✓ Stock symbols: {loader.stock_symbols}")
    print(f"  ✓ All symbols count: {len(loader.all_symbols)}")
    print(f"  ✓ SMA periods: {loader.indicators.SMA.periods}")
    print()


def test_dagster_config():
    print("Testing DagsterConfigLoader...")
    loader = DagsterConfigLoader()
    
    assert loader.module_name == "price_app"
    assert len(loader.asset_modules) > 0
    
    print(f"  ✓ Module name: {loader.module_name}")
    print(f"  ✓ Asset modules: {loader.asset_modules}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Config Loader Tests")
    print("=" * 60)
    print()
    
    try:
        test_app_config()
        test_asset_config()
        test_dagster_config()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
