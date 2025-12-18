"""Configuration loader with validation."""

from pathlib import Path
from omegaconf import OmegaConf
from typing import Dict, Any
import os

# Setup paths
ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
DOMAIN_CONFIG_FILE = CONFIG_DIR / "domain_config.yaml"
INFRASTRUCTURE_CONFIG_FILE = CONFIG_DIR / "infrastructure_config.yaml"

# Set environment variable for project root
os.environ["PROJECT_ROOT"] = str(ROOT)


class Settings:
    """Application settings with domain and infrastructure separation."""

    def __init__(self):
        """Load configuration files."""
        self.domain_config = OmegaConf.load(DOMAIN_CONFIG_FILE)
        self.infrastructure_config = OmegaConf.load(INFRASTRUCTURE_CONFIG_FILE)
        
        # Merge for backward compatibility
        self.config = OmegaConf.merge(self.domain_config, self.infrastructure_config)

    @property
    def domain(self) -> Dict[str, Any]:
        """Get domain configuration."""
        return OmegaConf.to_container(self.domain_config, resolve=True)

    @property
    def infrastructure(self) -> Dict[str, Any]:
        """Get infrastructure configuration."""
        return OmegaConf.to_container(self.infrastructure_config, resolve=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return OmegaConf.select(self.config, key, default=default)

    def get_domain(self, key: str, default: Any = None) -> Any:
        """Get a domain configuration value."""
        return OmegaConf.select(self.domain_config, key, default=default)

    def get_infrastructure(self, key: str, default: Any = None) -> Any:
        """Get an infrastructure configuration value."""
        return OmegaConf.select(self.infrastructure_config, key, default=default)


# Singleton instance
settings = Settings()

