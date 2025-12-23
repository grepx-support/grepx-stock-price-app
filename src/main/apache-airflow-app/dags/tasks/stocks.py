from config.asset_config import ASSET_CONFIG

def load_config(**ctx):
    ctx["ti"].xcom_push(key="symbols", value=ASSET_CONFIG["stocks"])

def fetch_prices(**ctx):
    symbols = ctx["ti"].xcom_pull(key="symbols")
    prices = [{"symbol": s, "price": 150.0} for s in symbols]
    ctx["ti"].xcom_push(key="prices", value=prices)

def compute_indicators(**ctx):
    prices = ctx["ti"].xcom_pull(key="prices")
    indicators = [{"symbol": p["symbol"], "SMA": 150, "EMA": 151} for p in prices]
    ctx["ti"].xcom_push(key="indicators", value=indicators)

def generate_report(**ctx):
    ctx["ti"].xcom_push(
        key="report",
        value={"asset": "stocks", "status": "SUCCESS"}
    )
