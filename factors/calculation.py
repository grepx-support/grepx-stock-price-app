from factors.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger,
    calculate_atr
)
from omegaconf import OmegaConf

cfg = OmegaConf.load("config/config.yaml")


def _macd_factors(df):
    """Compute MACD once, return all 3 values (no redundant calculations)"""
    macd, signal, hist = calculate_macd(
        df,
        cfg.indicators.MACD.fast,
        cfg.indicators.MACD.slow,
        cfg.indicators.MACD.signal
    )
    return {"macd": macd, "macd_signal": signal, "macd_hist": hist}


def _bollinger_factors(df):
    """Compute Bollinger Bands once, return all 3 values (no redundant calculations)"""
    upper, middle, lower = calculate_bollinger(
        df,
        cfg.indicators.BOLLINGER.period,
        cfg.indicators.BOLLINGER.std_dev
    )
    return {"bb_upper": upper, "bb_middle": middle, "bb_lower": lower}


FACTORS = {
    "ATR": lambda df: {"atr_14": calculate_atr(df, cfg.indicators.ATR.period)},
    "RSI": lambda df: {"rsi_14": calculate_rsi(df, cfg.indicators.RSI.period)},
    "MACD": _macd_factors,
    "SMA": lambda df: {f"sma_{p}": calculate_sma(df, p) for p in cfg.indicators.SMA.periods},
    "EMA": lambda df: {f"ema_{p}": calculate_ema(df, p) for p in cfg.indicators.EMA.periods},
    "BOLLINGER": _bollinger_factors
}

