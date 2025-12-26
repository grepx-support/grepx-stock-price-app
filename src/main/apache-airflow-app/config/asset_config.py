"""
Asset configuration for price orchestration pipelines.

This file defines the supported asset categories and their symbols.
It acts as a single source of truth for the assets processed by
Apache Airflow DAGs.

Structure:
    ASSET_CONFIG (dict[str, list[str]])
        - Key   : Asset type (e.g., stocks, indices, futures)
        - Value : List of symbols for that asset type

Usage:
    Task modules read from ASSET_CONFIG to determine
    which symbols to process.
"""

ASSET_CONFIG = {
    "stocks": ["AAPL", "GOOGL", "MSFT"],
    "indices": ["NIFTY50", "NIFTYNXT50"],
    "futures": ["NIFTYFUT", "BANKNIFTY"],
}