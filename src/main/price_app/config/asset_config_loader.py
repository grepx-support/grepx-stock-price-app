"""Asset configuration loader."""

from typing import Optional, List

from .config_loader import ConfigLoader
from .schemas import AssetConfig


class AssetConfigLoader:
    """Dedicated loader for asset configuration."""

    def __init__(self, config_dir: Optional[str] = None):
        self.loader = ConfigLoader(config_dir)
        self._config: Optional[AssetConfig] = None

    @property
    def config(self) -> AssetConfig:
        """Get cached asset config, loading if necessary."""
        if self._config is None:
            self._config = self.loader.load_asset_config()
        return self._config

    def reload(self) -> AssetConfig:
        """Force reload configuration."""
        self.loader.cleanup()
        self._config = self.loader.load_asset_config()
        return self._config

    # Convenience properties for asset types
    @property
    def stock_symbols(self) -> List[str]:
        return self.config.asset_types.stocks.symbols

    @property
    def index_symbols(self) -> List[str]:
        return self.config.asset_types.indices.symbols

    @property
    def futures_symbols(self) -> List[str]:
        return self.config.asset_types.futures.symbols

    @property
    def all_symbols(self) -> List[str]:
        """Get all symbols across all asset types."""
        return (
                self.stock_symbols +
                self.index_symbols +
                self.futures_symbols
        )

    # Date properties
    @property
    def start_date(self) -> str:
        return self.config.start_date

    @property
    def end_date(self) -> str:
        return self.config.end_date

    # Indicator properties
    @property
    def indicators(self):
        return self.config.indicators

    # Column mapping
    @property
    def columns(self):
        return self.config.columns

    # Naming convention
    @property
    def naming_convention(self):
        return self.config.naming_convention
