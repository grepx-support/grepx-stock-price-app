"""Simple tests for AppConfigLoader."""

import sys
import unittest
from pathlib import Path

from price_app.src.main.price_app.config import AppConfigLoader

# Add src/main to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))

class TestAppConfigLoader(unittest.TestCase):
    """Simple tests for AppConfigLoader."""
    
    def setUp(self):
        """Set up test loader."""
        self.loader = AppConfigLoader()
    
    def test_config_loads(self):
        """Test config loads successfully."""
        self.assertIsNotNone(self.loader.config)
    
    def test_app_name(self):
        """Test app name."""
        self.assertEqual(self.loader.config.app.name, "price_app")
    
    def test_celery_broker(self):
        """Test celery broker exists."""
        self.assertIsNotNone(self.loader.celery_config.broker_url)
    
    def test_task_modules(self):
        """Test task modules list."""
        self.assertGreater(len(self.loader.task_modules), 0)
    
    def test_database_config(self):
        """Test database config exists."""
        self.assertIsNotNone(self.loader.database_config.connection_string)


if __name__ == "__main__":
    unittest.main()
