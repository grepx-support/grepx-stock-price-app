"""Quick test script for config loader."""

import sys
from pathlib import Path

from price_app.src.main.price_app.config import ConfigLoader

# Add src/main to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))


def test_app_config():
    print("Testing App Config...")
    loader = ConfigLoader()
    
    cfg = loader.load_app_config()
    
    assert cfg.app.name == "price_app"
    assert cfg.celery.broker_url
    assert len(cfg.tasks.modules) > 0
    
    print(f"  ✓ App name: {cfg.app.name}")
    print(f"  ✓ Celery broker: {cfg.celery.broker_url}")
    print(f"  ✓ Task modules: {len(cfg.tasks.modules)}")
    print()


def test_asset_config():
    print("Testing Asset Config...")
    loader = ConfigLoader()
    
    cfg = loader.load_asset_config()
    
    assert len(cfg.asset_types.stocks.symbols) > 0
    assert cfg.indicators.SMA.periods
    
    print(f"  ✓ Stock symbols: {cfg.asset_types.stocks.symbols}")
    print(f"  ✓ SMA periods: {cfg.indicators.SMA.periods}")
    print()


def test_dagster_config():
    print("Testing Dagster Config...")
    loader = ConfigLoader()
    
    cfg = loader.load_dagster_config()
    
    assert cfg.dagster.module_name == "price_app"
    assert len(cfg.assets.modules) > 0
    
    print(f"  ✓ Module name: {cfg.dagster.module_name}")
    print(f"  ✓ Asset modules: {cfg.assets.modules}")
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
