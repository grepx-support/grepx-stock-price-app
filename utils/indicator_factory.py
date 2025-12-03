"""Factory utility for creating indicator instances."""
import logging
from config.indicators_config import INDICATORS_CONFIG, ENABLED_INDICATORS
from factors import ATR, EMA, SMA, BOLLINGER, MACD, RSI

logger = logging.getLogger(__name__)


INDICATOR_CLASSES = {
    "ATR": ATR,
    "EMA": EMA,
    "SMA": SMA,
    "BOLLINGER": BOLLINGER,
    "MACD": MACD,
    "RSI": RSI,
}


def create_indicator(indicator_name: str, symbol: str) -> object:
    """Create indicator instance based on name and config."""
    try:
        if indicator_name not in ENABLED_INDICATORS:
            logger.error(f"Indicator '{indicator_name}' is not enabled")
            raise ValueError(f"Indicator '{indicator_name}' is not enabled")

        if indicator_name not in INDICATOR_CLASSES:
            logger.error(f"Indicator '{indicator_name}' class not found")
            raise ValueError(f"Indicator '{indicator_name}' class not found")

        config = INDICATORS_CONFIG.get(indicator_name, {})
        indicator_class = INDICATOR_CLASSES[indicator_name]

        indicator = indicator_class(symbol, config)
        logger.info(f"Created {indicator_name} indicator for {symbol}")
        return indicator

    except Exception as e:
        logger.error(f"Failed to create indicator '{indicator_name}': {str(e)}", exc_info=True)
        raise


def get_enabled_indicators() -> list:
    """Get list of enabled indicators."""
    return ENABLED_INDICATORS