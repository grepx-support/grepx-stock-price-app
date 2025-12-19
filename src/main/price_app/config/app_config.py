"""Application configuration loader."""

from typing import Optional

from .loader import ConfigLoader
from .schemas import AppConfig


class AppConfigLoader:
    """Dedicated loader for application configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        self.loader = ConfigLoader(config_dir)
        self._config: Optional[AppConfig] = None

    @property
    def config(self) -> AppConfig:
        """Get cached app config, loading if necessary."""
        if self._config is None:
            self._config = self.loader.load_app_config()
        return self._config

    def reload(self) -> AppConfig:
        """Force reload configuration."""
        self.loader.cleanup()
        self._config = self.loader.load_app_config()
        return self._config

    # Convenience properties
    @property
    def celery_config(self):
        return self.config.celery

    @property
    def worker_config(self):
        return self.config.worker

    @property
    def task_config(self):
        return self.config.task

    @property
    def database_config(self):
        return self.config.database

    @property
    def task_modules(self):
        return self.config.tasks.modules
