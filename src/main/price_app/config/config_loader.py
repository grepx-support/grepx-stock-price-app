"""Hydra-based configuration loader."""

from pathlib import Path
from typing import Optional, Type, get_origin, get_args
from dataclasses import fields, is_dataclass
from omegaconf import OmegaConf, DictConfig
from omegaconf.errors import InterpolationResolutionError
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra

from .schemas import AppConfig, AssetConfig, DagsterConfig


def _dict_to_dataclass(cls: Type, data: dict):
    """
    Recursively convert a dictionary to a dataclass instance.
    
    Args:
        cls: The dataclass type to convert to
        data: Dictionary containing the data
        
    Returns:
        Instance of the dataclass with nested structures properly converted
    """
    if not is_dataclass(cls):
        return data
    
    field_types = {f.name: f.type for f in fields(cls)}
    kwargs = {}
    
    for field_name, field_type in field_types.items():
        if field_name not in data:
            continue
            
        value = data[field_name]
        
        # Handle nested dataclasses
        if is_dataclass(field_type):
            if isinstance(value, dict):
                kwargs[field_name] = _dict_to_dataclass(field_type, value)
            else:
                kwargs[field_name] = value
        # Handle lists of dataclasses
        elif get_origin(field_type) is list:
            args = get_args(field_type)
            if args and is_dataclass(args[0]) and isinstance(value, list):
                kwargs[field_name] = [
                    _dict_to_dataclass(args[0], item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                kwargs[field_name] = value
        else:
            kwargs[field_name] = value
    
    return cls(**kwargs)


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
        
        # Resolve variables and convert to dict, then to structured config
        # Fall back to unresolved if env vars are missing
        try:
            config_dict = OmegaConf.to_container(cfg, resolve=True)
        except InterpolationResolutionError:
            config_dict = OmegaConf.to_container(cfg, resolve=False)
        
        return _dict_to_dataclass(AppConfig, config_dict)
    
    def load_asset_config(self) -> AssetConfig:
        """
        Load asset configuration from asset.yaml.
        
        Returns:
            AssetConfig object with typed configuration
        """
        self._initialize_hydra()
        
        cfg = compose(config_name="asset")
        
        # Resolve variables and convert to dict, then to structured config
        # Fall back to unresolved if env vars are missing
        try:
            config_dict = OmegaConf.to_container(cfg, resolve=True)
        except InterpolationResolutionError:
            config_dict = OmegaConf.to_container(cfg, resolve=False)
        
        return _dict_to_dataclass(AssetConfig, config_dict)
    
    def load_dagster_config(self) -> DagsterConfig:
        """
        Load Dagster configuration from dagster.yaml.
        
        Returns:
            DagsterConfig object with typed configuration
        """
        self._initialize_hydra()
        
        cfg = compose(config_name="dagster")
        
        # Try to resolve variables, fall back to unresolved if env vars are missing
        # This handles cases where environment variables referenced in config are not set
        try:
            config_dict = OmegaConf.to_container(cfg, resolve=True)
        except InterpolationResolutionError:
            # If resolution fails (e.g., missing env vars), use unresolved version
            # Unresolved interpolations will remain as strings (e.g., "${oc.env:PROJECT_ROOT}/...")
            config_dict = OmegaConf.to_container(cfg, resolve=False)
        
        return _dict_to_dataclass(DagsterConfig, config_dict)
    
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
