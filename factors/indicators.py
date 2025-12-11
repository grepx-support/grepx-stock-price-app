# price_app/factors/indicators.py
"""
TA-Lib based technical indicators (10x faster than Pandas)
All functions return numpy arrays compatible with DataFrame assignment
TA-Lib: Industry-standard C library used by Bloomberg, JPMorgan, etc.
"""
import pandas as pd
import talib


def calculate_sma(df: pd.DataFrame, period: int):
    """Simple Moving Average - O(n) vectorized with TA-Lib"""
    return talib.SMA(df['close'].values, timeperiod=period)


def calculate_ema(df: pd.DataFrame, period: int):
    """Exponential Moving Average - 10x faster than Pandas ewm()"""
    return talib.EMA(df['close'].values, timeperiod=period)


def calculate_rsi(df: pd.DataFrame, period: int = 14):
    """Relative Strength Index - C-compiled calculation"""
    return talib.RSI(df['close'].values, timeperiod=period)


def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    """MACD (Moving Average Convergence Divergence)"""
    return talib.MACD(
        df['close'].values,
        fastperiod=fast,
        slowperiod=slow,
        signalperiod=signal
    )


def calculate_bollinger(df: pd.DataFrame, period=20, std_dev=2):
    """Bollinger Bands - Upper, Middle (SMA), Lower"""
    return talib.BBANDS(
        df['close'].values,
        timeperiod=period,
        nbdevup=std_dev,
        nbdevdn=std_dev,
        matype=talib.MA_Type.SMA
    )


def calculate_atr(df: pd.DataFrame, period=14):
    """Average True Range - Volatility indicator"""
    return talib.ATR(
        df['high'].values,
        df['low'].values,
        df['close'].values,
        timeperiod=period
    )