"""Configuration loader."""

from pathlib import Path
from omegaconf import OmegaConf, DictConfig


class ConfigLoader:
    """Loads all configuration files."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
    
    def load_all(self) -> DictConfig:
        """Load all configuration files."""
        app_config = OmegaConf.load(self.config_dir / "app.yaml")
        
        if hasattr(app_config, 'connections'):
            for conn in app_config.connections:
                if conn.get('enabled', True):
                    config_file = conn.config_file
                    conn_config = OmegaConf.load(self.config_dir / config_file)
                    app_config = OmegaConf.merge(app_config, conn_config)
        
        return app_config
