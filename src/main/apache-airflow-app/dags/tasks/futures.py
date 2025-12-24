from config.asset_config import ASSET_CONFIG


def load_config(**ctx):
    """
    Load futures symbols from the central asset configuration.

    Pushes the list of futures symbols to XCom so that
    downstream tasks can consume them.
    """
    ctx["ti"].xcom_push(key="symbols", value=ASSET_CONFIG["futures"])


def fetch_prices(**ctx):
    """
    Fetch price data for futures symbols.

    Pulls the symbols from XCom and pushes mock price
    data for each symbol to XCom.
    """
    symbols = ctx["ti"].xcom_pull(key="symbols")
    ctx["ti"].xcom_push(
        key="prices",
        value=[{"symbol": s, "price": 250.0} for s in symbols],
    )


def compute_indicators(**ctx):
    """
    Compute technical indicators for futures prices.

    Pulls price data from XCom and pushes derived
    indicator values (e.g., EMA) to XCom.
    """
    prices = ctx["ti"].xcom_pull(key="prices")
    ctx["ti"].xcom_push(
        key="indicators",
        value=[{"symbol": p["symbol"], "EMA": 251} for p in prices],
    )


def generate_report(**ctx):
    """
    Generate a summary report for futures processing.

    Pushes a simple report marker to XCom to indicate
    successful completion of the futures workflow.
    """
    ctx["ti"].xcom_push(key="report", value={"asset": "futures"})
