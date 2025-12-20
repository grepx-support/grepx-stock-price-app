import pandas as pd
import talib
from servers.factors.config import close

def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    return talib.MACD(
        df[close].values,
        fastperiod=fast,
        slowperiod=slow,
        signalperiod=signal
    )
