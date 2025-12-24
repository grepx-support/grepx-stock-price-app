from config.asset_config import ASSET_CONFIG


def load_config(**ctx):
    """
    Load stock symbols from the central asset configuration.

    Pushes the list of stock symbols to XCom so that
    downstream tasks can consume them.
    """
    ctx["ti"].xcom_push(key="symbols", value=ASSET_CONFIG["stocks"])


def fetch_prices(**ctx):
    """
    Fetch price data for stock symbols.

    Pulls the symbols from XCom and pushes mock price
    data for each stock symbol to XCom.
    """
    symbols = ctx["ti"].xcom_pull(key="symbols")
    prices = [{"symbol": s, "price": 150.0} for s in symbols]
    ctx["ti"].xcom_push(key="prices", value=prices)


def compute_indicators(**ctx):
    """
    Compute technical indicators for stock prices.

    Pulls price data from XCom and pushes derived
    indicator values (e.g., SMA, EMA) to XCom.
    """
    prices = ctx["ti"].xcom_pull(key="prices")
    indicators = [
        {"symbol": p["symbol"], "SMA": 150, "EMA": 151}
        for p in prices
    ]
    ctx["ti"].xcom_push(key="indicators", value=indicators)


def generate_report(**ctx):
    """
    Generate a summary report for stock processing.

    Pushes a simple report marker to XCom to indicate
    successful completion of the stocks workflow.
    """
    ctx["ti"].xcom_push(key="report", value={"asset": "stocks"})
