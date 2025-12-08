from typing import List
from dagster import asset
from dagster import asset, AssetExecutionContext


@asset(group_name="stocks")
def stock_symbols() -> List[str]:
    """Stock symbols to track"""
    return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]


@asset(group_name="stocks", deps=[stock_symbols])
def fetch_stock_prices(stock_symbols: List[str]):
    """Trigger price fetch tasks"""
    from tasks.stock_tasks import fetch_stock_price

    return [fetch_stock_price.delay(symbol).id for symbol in stock_symbols]


@asset(group_name="stocks", deps=[fetch_stock_prices])
def stored_stock_prices(stock_symbols: List[str]):
    """Verify prices stored in DB"""
    from app.main import mongo_app

    collection = mongo_app.instance.collection("stock_prices")
    today = datetime.now().date().isoformat()

    return collection.count_documents({
        "symbol": {"$in": stock_symbols},
        "date": today
    })
