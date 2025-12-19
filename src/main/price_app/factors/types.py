from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class MissingValueConfig:
    text: str
    numeric: Optional[float]

@dataclass
class ColumnConfig:
    high: str
    low: str
    close: str
    open: str
    volume: str