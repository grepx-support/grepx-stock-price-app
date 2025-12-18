"""Indicator result value objects."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional
from domain.exceptions import InvalidIndicatorError


@dataclass(frozen=True)
class IndicatorMetadata:
    """Metadata about an indicator calculation."""
    indicator_name: str
    symbol: str
    parameters: Dict[str, Any]

    def __post_init__(self):
        """Validate indicator metadata."""
        if not self.indicator_name or not self.indicator_name.strip():
            raise InvalidIndicatorError("Indicator name cannot be empty")
        if not self.symbol or not self.symbol.strip():
            raise InvalidIndicatorError("Symbol cannot be empty")


@dataclass(frozen=True)
class IndicatorResult:
    """Indicator calculation result for a specific date."""
    metadata: IndicatorMetadata
    date: date
    values: Dict[str, Any]  # e.g., {"sma_20": 150.5, "sma_50": 145.2}

    def __post_init__(self):
        """Validate indicator result."""
        if not self.values:
            raise InvalidIndicatorError("Indicator values cannot be empty")

