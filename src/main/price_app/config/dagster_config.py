"""Dagster configuration loader."""

from typing import Optional, List

from .loader import ConfigLoader
from .schemas import DagsterConfig

class DagsterConfigLoader:
    """Dedicated loader for Dagster configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        self.loader = ConfigLoader(config_dir)
        self._config: Optional[DagsterConfig] = None

    @property
    def config(self) -> DagsterConfig:
        """Get cached dagster config, loading if necessary."""
        if self._config is None:
            self._config = self.loader.load_dagster_config()
        return self._config

    def reload(self) -> DagsterConfig:
        """Force reload configuration."""
        self.loader.cleanup()
        self._config = self.loader.load_dagster_config()
        return self._config

    # Convenience properties
    @property
    def module_name(self) -> str:
        return self.config.dagster.module_name

    @property
    def dagster_home(self) -> str:
        return self.config.dagster.home

    @property
    def asset_modules(self) -> List[str]:
        return self.config.assets.modules

    @property
    def asset_directories(self) -> List[str]:
        return self.config.assets.directories

    @property
    def jobs(self):
        return self.config.jobs

    @property
    def ops(self):
        return self.config.ops
