"""Naming service for generating collection and database names."""

from typing import Dict, Any
from config.settings import settings


class NamingService:
    """Service for generating collection and database names."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with configuration."""
        self.config = config or settings.get_domain("naming_convention", {})

    def _apply_case(self, value: str, case_mode: str) -> str:
        """Apply case transformation."""
        if case_mode == "lower":
            return value.lower()
        elif case_mode == "upper":
            return value.upper()
        elif case_mode == "mixed":
            return value.capitalize()
        else:
            return value

    def get_analysis_db_name(self, asset_type: str) -> str:
        """Get database name for asset type."""
        db_map = {
            "stocks": "stocks_analysis",
            "indices": "indices_analysis",
            "futures": "futures_analysis",
        }
        db_name = db_map.get(asset_type.lower())
        if not db_name:
            raise ValueError(f"Unknown asset_type: {asset_type}")
        return db_name

    def get_price_collection_name(self, asset_type: str, symbol: str) -> str:
        """Get price collection name."""
        case_mode = self.config.get("case_mode", "lower")
        separator = self.config.get("separator", "_")
        template = self.config.get("price_template", "{symbol}{sep}prices")

        symbol = self._apply_case(symbol, case_mode)
        collection_name = template.format(symbol=symbol, sep=separator)
        return collection_name

    def get_indicator_collection_name(self, asset_type: str, symbol: str, factor: str) -> str:
        """Get indicator collection name."""
        case_mode = self.config.get("case_mode", "lower")
        separator = self.config.get("separator", "_")
        template = self.config.get("indicator_template", "{symbol}{sep}{factor}")

        symbol = self._apply_case(symbol, case_mode)
        factor = self._apply_case(factor, case_mode)
        collection_name = template.format(symbol=symbol, factor=factor, sep=separator)
        return collection_name


# Singleton instance
naming_service = NamingService()

