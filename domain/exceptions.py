"""Domain exceptions - pure business logic errors."""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class InvalidPriceDataError(DomainException):
    """Raised when price data is invalid."""
    pass


class InvalidIndicatorError(DomainException):
    """Raised when indicator calculation fails."""
    pass


class InvalidAssetError(DomainException):
    """Raised when asset information is invalid."""
    pass


class InsufficientDataError(DomainException):
    """Raised when there's not enough data for calculation."""
    pass

