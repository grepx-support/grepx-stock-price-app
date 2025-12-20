"""Test connection_registry.py"""

import sys
import unittest
from pathlib import Path

from price_app.src.main.servers.connections.connection_registry import ConnectionRegistry

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))

class TestConnectionRegistry(unittest.TestCase):
    def test_register(self):
        registry = ConnectionRegistry()
        registry.register("test", "value")
        self.assertTrue(registry.has("test"))
    
    def test_get(self):
        registry = ConnectionRegistry()
        registry.register("test", "value")
        self.assertEqual(registry.get("test"), "value")
    
    def test_clear(self):
        registry = ConnectionRegistry()
        registry.register("test", "value")
        registry.clear()
        self.assertFalse(registry.has("test"))

if __name__ == "__main__":
    unittest.main()
