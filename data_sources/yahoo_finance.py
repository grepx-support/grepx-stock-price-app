"""Yahoo Finance data fetcher."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class YahooFinanceAPI:
    """Fetch stock data from Yahoo Finance."""

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        logger.info("Initialized Yahoo Finance API for %s", ticker)

    def fetch_historical_prices(
        self, start_date: str, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        logger.info("Fetching %s data from %s to %s", self.ticker, start_date, end_date)

        df = self.stock.history(start=start_date, end=end_date)
        if df.empty:
            logger.warning("No data found for %s", self.ticker)
            return pd.DataFrame()

        df = df.rename(
            columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
        )
        df["adjusted_close"] = df["close"]
        df = df.reset_index()
        df["date"] = pd.to_datetime(df["Date"]).dt.date

        df = df[["date", "open", "high", "low", "close", "volume", "adjusted_close"]]
        df["volume"] = df["volume"].astype(int)
        logger.info("Fetched %s rows for %s", len(df), self.ticker)
        return df

    def fetch_latest_price(self) -> Optional[Dict[str, Any]]:
        today = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        df = self.fetch_historical_prices(start, today)
        if df.empty:
            return None
        return df.iloc[-1].to_dict()

    def fetch_company_info(self) -> Dict[str, Any]:
        info = self.stock.info
        return {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "shares_outstanding": info.get("sharesOutstanding"),
        }

