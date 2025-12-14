import pandas as pd
import talib
from factors.config import high, low, close

def calculate_atr(df: pd.DataFrame, period=14):
    return talib.ATR(
        df[high].values,
        df[low].values,
        df[close].values,
        timeperiod=period
    )
