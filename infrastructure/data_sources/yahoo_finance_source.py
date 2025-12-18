"""Yahoo Finance implementation of market data source."""

import yfinance as yf
from datetime import datetime
from typing import Optional
from application.ports.data_sources import IMarketDataSource
from application.dto import FetchPricesResultDTO
import logging

logger = logging.getLogger(__name__)


class YahooFinanceDataSource(IMarketDataSource):
    """Yahoo Finance implementation of market data source."""

    def fetch_prices(self, symbol: str, start_date: str = None, end_date: str = None) -> FetchPricesResultDTO:
        """Fetch stock prices from Yahoo Finance."""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                return FetchPricesResultDTO(
                    symbol=symbol,
                    records=[],
                    count=0,
                    status="no_data",
                    error="No data returned from Yahoo Finance"
                )
            
            records = []
            for date, row in data.iterrows():
                records.append({
                    "symbol": symbol,
                    "date": str(date.date()),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                    "fetched_at": datetime.now().isoformat(),
                })
            
            return FetchPricesResultDTO(
                symbol=symbol,
                records=records,
                count=len(records),
                status="success"
            )
            
        except Exception as e:
            logger.error(f"Error fetching prices for {symbol}: {e}")
            return FetchPricesResultDTO(
                symbol=symbol,
                records=[],
                count=0,
                status="error",
                error=str(e)
            )

    def fetch_multiple_prices(self, symbols: list, start_date: str = None, end_date: str = None) -> dict:
        """Fetch price data for multiple symbols."""
        results = {}
        for symbol in symbols:
            results[symbol] = self.fetch_prices(symbol, start_date, end_date)
        return results

