"""Hydra-based configuration loader."""

from pathlib import Path
from typing import Optional
from dataclasses import fields
from omegaconf import OmegaConf, DictConfig
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra

from .schemas import AppConfig, AssetConfig, DagsterConfig


class ConfigLoader:
    """Load configurations using Hydra Core."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_dir: Path to config directory. If None, uses default resources path.
        """
        if config_dir is None:
            # Default to resources directory
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
            # Clear any existing Hydra instance
            GlobalHydra.instance().clear()
            
            # Initialize with absolute config directory
            initialize_config_dir(
                version_base=None,
                config_dir=str(self.config_dir)
            )
            self._initialized = True
    
    def load_app_config(self) -> AppConfig:
        """
        Load application configuration from app.yaml.
        
        Returns:
            AppConfig object with typed configuration
        """
        self._initialize_hydra()
        
        cfg = compose(config_name="app")
        
        # Convert to container (dict) then to structured config
        config_dict = OmegaConf.to_container(cfg, resolve=True)
        return OmegaConf.structured(AppConfig(**config_dict))
    
    def load_asset_config(self) -> AssetConfig:
        """
        Load asset configuration from asset.yaml.
        
        Returns:
            AssetConfig object with typed configuration
        """
        self._initialize_hydra()
        
        cfg = compose(config_name="asset")
        
        config_dict = OmegaConf.to_container(cfg, resolve=True)
        return OmegaConf.structured(AssetConfig(**config_dict))
    
    def load_dagster_config(self) -> DagsterConfig:
        """
        Load Dagster configuration from dagster.yaml.
        
        Returns:
            DagsterConfig object with typed configuration
        """
        self._initialize_hydra()
        
        cfg = compose(config_name="dagster")
        
        config_dict = OmegaConf.to_container(cfg, resolve=True)
        return OmegaConf.structured(DagsterConfig(**config_dict))
    
    def load_all(self) -> tuple[AppConfig, AssetConfig, DagsterConfig]:
        """
        Load all configurations.
        
        Returns:
            Tuple of (AppConfig, AssetConfig, DagsterConfig)
        """
        return (
            self.load_app_config(),
            self.load_asset_config(),
            self.load_dagster_config()
        )
    
    def load_raw(self, config_name: str) -> DictConfig:
        """
        Load raw configuration without type conversion.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            
        Returns:
            DictConfig object from Hydra
        """
        self._initialize_hydra()
        return compose(config_name=config_name)
    
    @staticmethod
    def override_config(cfg: DictConfig, overrides: dict) -> DictConfig:
        """
        Override configuration values.
        
        Args:
            cfg: Configuration to override
            overrides: Dictionary of overrides (dot notation supported)
            
        Returns:
            Updated configuration
        """
        return OmegaConf.merge(cfg, overrides)
    
    def cleanup(self):
        """Clean up Hydra instance."""
        if self._initialized:
            GlobalHydra.instance().clear()
            self._initialized = False
