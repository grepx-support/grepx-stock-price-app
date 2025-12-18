"""Pure indicator calculation logic - no external dependencies."""

import pandas as pd
import talib
from typing import Dict, Any, List
from datetime import date
import polars as pl

from domain.models.indicator import IndicatorResult, IndicatorMetadata
from domain.models.price import PriceData
from domain.exceptions import InvalidIndicatorError, InsufficientDataError


class IndicatorCalculator:
    """Pure calculation logic for technical indicators."""

    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        if len(df) < period:
            raise InsufficientDataError(f"Need at least {period} data points for SMA")
        return pd.Series(talib.SMA(df['close'].values, timeperiod=period), index=df.index)

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        if len(df) < period:
            raise InsufficientDataError(f"Need at least {period} data points for EMA")
        return pd.Series(talib.EMA(df['close'].values, timeperiod=period), index=df.index)

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        if len(df) < period + 1:
            raise InsufficientDataError(f"Need at least {period + 1} data points for RSI")
        return pd.Series(talib.RSI(df['close'].values, timeperiod=period), index=df.index)

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(df) < slow:
            raise InsufficientDataError(f"Need at least {slow} data points for MACD")
        macd, signal_line, histogram = talib.MACD(
            df['close'].values,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )
        return {
            'macd': pd.Series(macd, index=df.index),
            'signal': pd.Series(signal_line, index=df.index),
            'histogram': pd.Series(histogram, index=df.index)
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        if len(df) < period:
            raise InsufficientDataError(f"Need at least {period} data points for ATR")
        return pd.Series(
            talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period),
            index=df.index
        )

    @staticmethod
    def calculate_bollinger(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        if len(df) < period:
            raise InsufficientDataError(f"Need at least {period} data points for Bollinger Bands")
        upper, middle, lower = talib.BBANDS(
            df['close'].values,
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev,
            matype=talib.MA_Type.SMA
        )
        return {
            'upper': pd.Series(upper, index=df.index),
            'middle': pd.Series(middle, index=df.index),
            'lower': pd.Series(lower, index=df.index)
        }

    @staticmethod
    def compute_indicator(
        symbol: str,
        indicator_name: str,
        price_records: List[Dict[str, Any]],
        parameters: Dict[str, Any],
        missing_value_text: str = "no data available"
    ) -> List[Dict[str, Any]]:
        """
        Compute indicator values from price records.
        
        Returns list of dictionaries with indicator values per date.
        """
        if not price_records:
            return []

        # Convert to Polars DataFrame for efficient processing
        df = pl.DataFrame(price_records)
        df = df.with_columns(pl.col('date').cast(pl.Date)).sort('date')

        # Convert to pandas for talib
        df_pandas = df.to_pandas()
        df_pandas.set_index('date', inplace=True)

        # Calculate indicator based on name
        factor_cols = {}
        
        if indicator_name == "SMA":
            periods = parameters.get('periods', [20])
            for period in periods:
                series = IndicatorCalculator.calculate_sma(df_pandas, period)
                factor_cols[f"sma_{period}"] = series.values

        elif indicator_name == "EMA":
            periods = parameters.get('periods', [12, 26])
            for period in periods:
                series = IndicatorCalculator.calculate_ema(df_pandas, period)
                factor_cols[f"ema_{period}"] = series.values

        elif indicator_name == "RSI":
            period = parameters.get('period', 14)
            series = IndicatorCalculator.calculate_rsi(df_pandas, period)
            factor_cols['rsi'] = series.values

        elif indicator_name == "MACD":
            fast = parameters.get('fast', 12)
            slow = parameters.get('slow', 26)
            signal = parameters.get('signal', 9)
            macd_data = IndicatorCalculator.calculate_macd(df_pandas, fast, slow, signal)
            factor_cols['macd'] = macd_data['macd'].values
            factor_cols['macd_signal'] = macd_data['signal'].values
            factor_cols['macd_histogram'] = macd_data['histogram'].values

        elif indicator_name == "ATR":
            period = parameters.get('period', 14)
            series = IndicatorCalculator.calculate_atr(df_pandas, period)
            factor_cols['atr'] = series.values

        elif indicator_name == "BOLLINGER":
            period = parameters.get('period', 20)
            std_dev = parameters.get('std_dev', 2.0)
            bb_data = IndicatorCalculator.calculate_bollinger(df_pandas, period, std_dev)
            factor_cols['bb_upper'] = bb_data['upper'].values
            factor_cols['bb_middle'] = bb_data['middle'].values
            factor_cols['bb_lower'] = bb_data['lower'].values

        else:
            raise InvalidIndicatorError(f"Unknown indicator: {indicator_name}")

        # Add columns to Polars DataFrame
        for col_name, col_data in factor_cols.items():
            df = df.with_columns(pl.Series(col_name, col_data))

        # Handle missing values
        factor_col_names = list(factor_cols.keys())
        for col in factor_col_names:
            df = df.with_columns(
                pl.when(pl.col(col).is_null() | pl.col(col).is_nan())
                .then(pl.lit(missing_value_text))
                .otherwise(pl.col(col).cast(pl.Utf8))
                .alias(col)
            )

        # Add metadata columns
        df = df.with_columns([
            pl.lit(symbol).alias('symbol'),
            pl.lit(indicator_name).alias('factor'),
            pl.col('date').cast(pl.Utf8).alias('date')
        ])

        # Select and return results
        results = df.select(['symbol', 'date'] + factor_col_names + ['factor']).to_dicts()
        return results

