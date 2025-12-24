from config.asset_config import ASSET_CONFIG


def load_config(**ctx):
    """
    Load index symbols from the central asset configuration.

    Pushes the list of index symbols to XCom so that
    downstream tasks can consume them.
    """
    ctx["ti"].xcom_push(key="symbols", value=ASSET_CONFIG["indices"])


def fetch_prices(**ctx):
    """
    Fetch price data for index symbols.

    Pulls the symbols from XCom and pushes mock price
    data for each index symbol to XCom.
    """
    symbols = ctx["ti"].xcom_pull(key="symbols")
    ctx["ti"].xcom_push(
        key="prices",
        value=[{"symbol": s, "price": 200.0} for s in symbols],
    )


def compute_indicators(**ctx):
    """
    Compute technical indicators for index prices.

    Pulls price data from XCom and pushes derived
    indicator values (e.g., SMA) to XCom.
    """
    prices = ctx["ti"].xcom_pull(key="prices")
    ctx["ti"].xcom_push(
        key="indicators",
        value=[{"symbol": p["symbol"], "SMA": 200} for p in prices],
    )


def generate_report(**ctx):
    """
    Generate a summary report for index processing.

    Pushes a simple report marker to XCom to indicate
    successful completion of the indices workflow.
    """
    ctx["ti"].xcom_push(key="report", value={"asset": "indices"})
