import pandas as pd
import talib
from factors.config import close

def calculate_rsi(df: pd.DataFrame, period: int = 14):
    return talib.RSI(df[close].values, timeperiod=period)
