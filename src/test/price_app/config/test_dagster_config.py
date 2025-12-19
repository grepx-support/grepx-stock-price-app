"""Simple tests for DagsterConfigLoader."""

import sys
import unittest
from pathlib import Path

from price_app.src.main.price_app.config import DagsterConfigLoader

# Add src/main to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))

class TestDagsterConfigLoader(unittest.TestCase):
    """Simple tests for DagsterConfigLoader."""
    
    def setUp(self):
        """Set up test loader."""
        self.loader = DagsterConfigLoader()
    
    def test_config_loads(self):
        """Test config loads successfully."""
        self.assertIsNotNone(self.loader.config)
    
    def test_module_name(self):
        """Test module name."""
        self.assertEqual(self.loader.module_name, "price_app")
    
    def test_asset_modules(self):
        """Test asset modules exist."""
        self.assertGreater(len(self.loader.asset_modules), 0)
    
    def test_dagster_home(self):
        """Test dagster home exists."""
        self.assertIsNotNone(self.loader.dagster_home)


if __name__ == "__main__":
    unittest.main()
