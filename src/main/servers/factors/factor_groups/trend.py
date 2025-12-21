from servers.factors.indicators.sma import calculate_sma
from servers.factors.indicators.ema import calculate_ema
from servers.factors.config import cfg

def sma_factors(df):
    return {
        f"sma_{p}": calculate_sma(df, p)
        for p in cfg.indicators.SMA.periods
    }


def ema_factors(df):
    return {
        f"ema_{p}": calculate_ema(df, p)
        for p in cfg.indicators.EMA.periods
    }
