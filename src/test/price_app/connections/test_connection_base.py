"""Test connection_base.py"""

import sys
import unittest
from pathlib import Path

from price_app.src.main.price_app.connections.connection_base import ConnectionBase
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "main"))

class MockConnection(ConnectionBase):
    def connect(self):
        self._client = "connected"
    
    def disconnect(self):
        self._client = None


class TestConnectionBase(unittest.TestCase):
    def test_connect(self):
        conn = MockConnection({})
        conn.connect()
        self.assertIsNotNone(conn._client)
    
    def test_is_connected(self):
        conn = MockConnection({})
        self.assertFalse(conn.is_connected())
        conn.connect()
        self.assertTrue(conn.is_connected())
    
    def test_get_client(self):
        conn = MockConnection({})
        client = conn.get_client()
        self.assertEqual(client, "connected")


if __name__ == "__main__":
    unittest.main()
