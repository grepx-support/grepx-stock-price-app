from factors.indicators.rsi import calculate_rsi
from factors.indicators.macd import calculate_macd
from factors.config import cfg


def rsi_factor(df):
    return {"rsi_14": calculate_rsi(df, cfg.indicators.RSI.period)}


def macd_factors(df):
    macd, signal, hist = calculate_macd(
        df,
        cfg.indicators.MACD.fast,
        cfg.indicators.MACD.slow,
        cfg.indicators.MACD.signal
    )
    return {
        "macd": macd,
        "macd_signal": signal,
        "macd_hist": hist
    }
