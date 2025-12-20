import pandas as pd
import talib
from servers.factors.config import close

def calculate_sma(df: pd.DataFrame, period: int):
    return talib.SMA(df[close].values, timeperiod=period)
