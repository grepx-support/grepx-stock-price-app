import pandas as pd
import talib
from servers.factors.config import close

def calculate_bollinger(df: pd.DataFrame, period=20, std_dev=2):
    return talib.BBANDS(
        df[close].values,
        timeperiod=period,
        nbdevup=std_dev,
        nbdevdn=std_dev,
        matype=talib.MA_Type.SMA
    )
