"""Price App - Main package."""
__all__ = [
    "ConfigLoader",
]

# Import only non-circular dependencies at module level
from servers.config.config_loader import ConfigLoader

# ConnectionManager has been moved to grepx-connection-registry library
# Import it directly: from grepx_connection_registry import ConnectionManager
