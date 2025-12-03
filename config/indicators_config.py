"""Configuration for technical indicators."""
from factors import ATR, EMA, SMA, BOLLINGER, MACD, RSI

INDICATORS_CONFIG = {
    "ATR": {
        "name": "Average True Range",
        "periods": [14, 21],
        "min_data_points": 14,
        "required_columns": ["high", "low", "close"],
    },
    "BOLLINGER": {
        "name": "Bollinger Bands",
        "periods": [20],
        "std_dev": [2],
        "min_data_points": 20,
        "required_columns": ["close"],
    },
    "EMA": {
        "name": "Exponential Moving Average",
        "periods": [12, 26, 50, 200],
        "min_data_points": 1,
        "required_columns": ["close"],
    },
    "SMA": {
        "name": "Simple Moving Average",
        "periods": [10, 20, 50, 200],
        "min_data_points": 1,
        "required_columns": ["close"],
    },
    "MACD": {
        "name": "MACD",
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
        "min_data_points": 26,
        "required_columns": ["close"],
    },
    "RSI": {
        "name": "Relative Strength Index",
        "periods": [14],
        "min_data_points": 14,
        "required_columns": ["close"],
    },
}

# Feature flags for indicators
ENABLED_INDICATORS = ["ATR", "BOLLINGER", "EMA", "SMA", "MACD", "RSI"]

# Mapping of indicator names to their implementation classes
INDICATOR_CLASSES = {
    "ATR": ATR,
    "EMA": EMA,
    "SMA": SMA,
    "BOLLINGER": BOLLINGER,
    "MACD": MACD,
    "RSI": RSI,
}
