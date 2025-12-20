from servers.factors.factor_groups.trend import sma_factors, ema_factors
from servers.factors.factor_groups.momentum import rsi_factor, macd_factors
from servers.factors.factor_groups.volatility import atr_factor, bollinger_factors

FACTORS = {
    "SMA": sma_factors,
    "EMA": ema_factors,
    "RSI": rsi_factor,
    "MACD": macd_factors,
    "ATR": atr_factor,
    "BOLLINGER": bollinger_factors
}
