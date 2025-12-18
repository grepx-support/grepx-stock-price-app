"""Asset and symbol value objects."""

from dataclasses import dataclass
from typing import List, Optional
from domain.exceptions import InvalidAssetError


@dataclass(frozen=True)
class Symbol:
    """Symbol value object."""
    value: str
    asset_type: str  # "stocks", "indices", "futures"

    def __post_init__(self):
        """Validate symbol."""
        if not self.value or not self.value.strip():
            raise InvalidAssetError("Symbol value cannot be empty")
        if self.asset_type not in ["stocks", "indices", "futures"]:
            raise InvalidAssetError(f"Invalid asset type: {self.asset_type}")


@dataclass(frozen=True)
class Asset:
    """Asset value object."""
    symbol: Symbol
    display_name: Optional[str] = None

    @property
    def symbol_value(self) -> str:
        """Get the symbol string value."""
        return self.symbol.value

    @property
    def asset_type(self) -> str:
        """Get the asset type."""
        return self.symbol.asset_type

