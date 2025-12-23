from config.asset_config import ASSET_CONFIG

def load_config(**ctx):
    ctx["ti"].xcom_push(key="symbols", value=ASSET_CONFIG["futures"])

def fetch_prices(**ctx):
    symbols = ctx["ti"].xcom_pull(key="symbols")
    ctx["ti"].xcom_push(
        key="prices",
        value=[{"symbol": s, "price": 250.0} for s in symbols]
    )

def compute_indicators(**ctx):
    prices = ctx["ti"].xcom_pull(key="prices")
    ctx["ti"].xcom_push(
        key="indicators",
        value=[{"symbol": p["symbol"], "EMA": 251} for p in prices]
    )

def generate_report(**ctx):
    ctx["ti"].xcom_push(key="report", value={"asset": "futures"})
