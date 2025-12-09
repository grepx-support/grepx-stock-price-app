# price_app/services/indicator_service.py
from datetime import datetime
from typing import Dict, List
import pandas as pd
from factors.indicators import (
    calculate_sma, calculate_ema, calculate_rsi,
    calculate_macd, calculate_bollinger, calculate_atr
)
from omegaconf import OmegaConf

# Load indicator config once
INDICATOR_CONFIG = OmegaConf.load("config/config.yaml").indicators

def compute_all_indicators(symbol: str, price_records: List[Dict]) -> List[Dict]:
    if not price_records:
        return []

    df = pd.DataFrame(price_records)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').set_index('date')

    results = []
    base = {
        "symbol": symbol,
        "source": "yfinance",
        "fetched_at": datetime.now().isoformat()
    }

    # SMA
    for p in INDICATOR_CONFIG.sma.periods:
        df[f"sma_{p}"] = calculate_sma(df, p)
    
    # EMA
    for p in INDICATOR_CONFIG.ema.periods:
        df[f"ema_{p}"] = calculate_ema(df, p)

    # RSI
    df["rsi_14"] = calculate_rsi(df, INDICATOR_CONFIG.rsi.period)

    # MACD
    macd_line, signal_line, hist = calculate_macd(df,
        INDICATOR_CONFIG.macd.fast,
        INDICATOR_CONFIG.macd.slow,
        INDICATOR_CONFIG.macd.signal)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist

    # Bollinger Bands
    upper, middle, lower = calculate_bollinger(df,
        INDICATOR_CONFIG.bollinger.period,
        INDICATOR_CONFIG.bollinger.std_dev)
    df["bb_upper"] = upper
    df["bb_middle"] = middle
    df["bb_lower"] = lower

    # ATR
    df["atr_14"] = calculate_atr(df, INDICATOR_CONFIG.atr.period)

    # Convert back to records
    # After all calculations
    df = df.reset_index()

    results = []
    for _, row in df.iterrows():
        record = {
        "symbol": symbol,
        "date": str(row['date'].date()),
        "source": "yfinance",
        "fetched_at": datetime.now().isoformat()
    }
        # Only copy indicator fields (everything except raw OHLCV + metadata)
        for col in df.columns:
            if col in {'date', 'open', 'high', 'low', 'close', 'volume', 'symbol', 'fetched_at'}:
                continue
            value = row[col]
            record[col] = float(value) if pd.notna(value) else None
        results.append(record)
    return results