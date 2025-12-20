import pandas as pd
import talib
from servers.factors.config import close

def calculate_ema(df: pd.DataFrame, period: int):
    return talib.EMA(df[close].values, timeperiod=period)
