"""Test connection_manager.py"""

import sys
import unittest
from pathlib import Path

from price_app.src.main.price_app.connections.connection_manager import ConnectionManager
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))

class TestConnectionManager(unittest.TestCase):
    
    def test_init(self):
        manager = ConnectionManager({}, "/test")
        self.assertIsNotNone(manager.registry)
    
    def test_disconnect_all(self):
        manager = ConnectionManager({}, "/test")
        manager.registry.register("test", "value")
        manager.disconnect_all()
        self.assertFalse(manager.registry.has("test"))

if __name__ == "__main__":
    unittest.main()
