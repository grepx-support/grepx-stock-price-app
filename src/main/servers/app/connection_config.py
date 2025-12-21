"""Connection configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConnectionConfig:
    """Default connection IDs."""
    database: str = "primary_db"
    celery: str = "primary_celery"
    dagster: str = "primary_dagster"
    
    @classmethod
    def from_config(cls, config):
        """Load from app config."""
        if hasattr(config, 'defaults'):
            return cls(
                database=config.defaults.get('database', 'primary_db'),
                celery=config.defaults.get('celery', 'primary_celery'),
                dagster=config.defaults.get('dagster', 'primary_dagster')
            )
        return cls()
