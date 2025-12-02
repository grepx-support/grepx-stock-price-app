from datetime import datetime
import pandas as pd
from nsepython import equity_history
import logging

logger = logging.getLogger(__name__)

class NSEAPI:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol.replace(".NS", "")
        logger.info(f"Initialized NSE API for {self.symbol}")

    def fetch_historical_prices(self, start_date: str, end_date: str = None) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.now().strftime("%d-%m-%Y")

        start_date_fmt = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        logger.info(f"Fetching NSE data for {self.symbol} from {start_date_fmt} to {end_date}")

        try:
            df = equity_history(self.symbol, "EQ", start_date_fmt, end_date)
        except Exception as e:
            logger.error(f"NSE fetch error for {self.symbol}: {e}")
            return pd.DataFrame()

        if df is None or df.empty:
            logger.warning(f"No data found for {self.symbol}")
            return pd.DataFrame()

        # Rename to your schema
        df = df.rename(columns={
            "CH_TIMESTAMP": "date",
            "CH_OPENING_PRICE": "open",
            "CH_TRADE_HIGH_PRICE": "high",
            "CH_TRADE_LOW_PRICE": "low",
            "CH_CLOSING_PRICE": "close",
            "CH_LAST_TRADED_PRICE": "adjusted_close",
            "CH_TOT_TRADED_QTY": "volume",
        })

        df["date"] = pd.to_datetime(df["date"]).dt.date

        # MOST IMPORTANT FIX: convert EVERYTHING to float
        numeric_cols = ["open", "high", "low", "close", "adjusted_close", "volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

        # Drop rows with missing price values (after conversion)
        df = df.dropna(subset=["open", "high", "low", "close"])

        df = df[["date", "open", "high", "low", "close", "volume", "adjusted_close"]]

        logger.info(f"Fetched {len(df)} rows from NSE for {self.symbol}")
        return df
