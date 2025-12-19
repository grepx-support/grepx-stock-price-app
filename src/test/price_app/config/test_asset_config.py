"""Simple tests for AssetConfigLoader."""

import sys
import unittest
from pathlib import Path

from price_app.src.main.price_app.config import AssetConfigLoader

# Add src/main to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))

class TestAssetConfigLoader(unittest.TestCase):
    """Simple tests for AssetConfigLoader."""
    
    def setUp(self):
        """Set up test loader."""
        self.loader = AssetConfigLoader()
    
    def test_config_loads(self):
        """Test config loads successfully."""
        self.assertIsNotNone(self.loader.config)
    
    def test_stock_symbols(self):
        """Test stock symbols exist."""
        self.assertGreater(len(self.loader.stock_symbols), 0)
    
    def test_all_symbols(self):
        """Test all symbols combined."""
        self.assertGreater(len(self.loader.all_symbols), 0)
    
    def test_sma_periods(self):
        """Test SMA indicator config."""
        self.assertIsNotNone(self.loader.indicators.SMA.periods)
    
    def test_date_range(self):
        """Test date range exists."""
        self.assertIsNotNone(self.loader.start_date)
        self.assertIsNotNone(self.loader.end_date)


if __name__ == "__main__":
    unittest.main()
