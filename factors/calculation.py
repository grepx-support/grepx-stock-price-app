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

FACTORS = {
    "ATR": lambda df: {"atr_14": calculate_atr(df, cfg.indicators.ATR.period)},
    "RSI": lambda df: {"rsi_14": calculate_rsi(df, cfg.indicators.RSI.period)},
    "MACD": lambda df: {
        "macd": calculate_macd(df, cfg.indicators.MACD.fast, cfg.indicators.MACD.slow, cfg.indicators.MACD.signal)[0],
        "macd_signal": calculate_macd(df, cfg.indicators.MACD.fast, cfg.indicators.MACD.slow, cfg.indicators.MACD.signal)[1],
        "macd_hist": calculate_macd(df, cfg.indicators.MACD.fast, cfg.indicators.MACD.slow, cfg.indicators.MACD.signal)[2]
    },
    "SMA": lambda df: {f"sma_{p}": calculate_sma(df, p) for p in cfg.indicators.SMA.periods},
    "EMA": lambda df: {f"ema_{p}": calculate_ema(df, p) for p in cfg.indicators.EMA.periods},
    "BOLLINGER": lambda df: {
        "bb_upper": calculate_bollinger(df, cfg.indicators.BOLLINGER.period, cfg.indicators.BOLLINGER.std_dev)[0],
        "bb_middle": calculate_bollinger(df, cfg.indicators.BOLLINGER.period, cfg.indicators.BOLLINGER.std_dev)[1],
        "bb_lower": calculate_bollinger(df, cfg.indicators.BOLLINGER.period, cfg.indicators.BOLLINGER.std_dev)[2]
    }
}

