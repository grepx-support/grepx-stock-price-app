"""Hydra-based configuration loader."""

from pathlib import Path
from typing import Optional
from omegaconf import OmegaConf, DictConfig
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra


class ConfigLoader:
    """Load configurations using Hydra Core."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize config loader."""
        if config_dir is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            config_dir = str(project_root.parent / "resources")
        
        self.config_dir = Path(config_dir).resolve()
        if not self.config_dir.exists():
            raise ValueError(f"Config directory does not exist: {self.config_dir}")
        
        self._initialized = False
    
    def _initialize_hydra(self):
        """Initialize Hydra with config directory."""
        if not self._initialized:
            GlobalHydra.instance().clear()
            initialize_config_dir(version_base=None, config_dir=str(self.config_dir))
            self._initialized = True
    
    def load_app_config(self):
        """Load application configuration from app.yaml."""
        self._initialize_hydra()
        return compose(config_name="app")
    
    def load_asset_config(self):
        """Load asset configuration from asset.yaml."""
        self._initialize_hydra()
        return compose(config_name="asset")
    
    def load_dagster_config(self):
        """Load Dagster configuration from dagster.yaml."""
        self._initialize_hydra()
        return compose(config_name="dagster")
    
    def load_all(self):
        """Load all configurations."""
        return (
            self.load_app_config(),
            self.load_asset_config(),
            self.load_dagster_config()
        )
    
    def load_raw(self, config_name: str) -> DictConfig:
        """Load raw configuration."""
        self._initialize_hydra()
        return compose(config_name=config_name)
    
    @staticmethod
    def override_config(cfg: DictConfig, overrides: dict) -> DictConfig:
        """Override configuration values."""
        return OmegaConf.merge(cfg, overrides)
    
    def cleanup(self):
        """Clean up Hydra instance."""
        if self._initialized:
            GlobalHydra.instance().clear()
            self._initialized = False
