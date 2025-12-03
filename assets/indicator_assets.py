"""Factory for creating indicator assets - submits Celery tasks."""
from dagster import asset, AssetIn, Failure
import logging
from config.paths import DAGSTER_CONFIG
from omegaconf import OmegaConf

logger = logging.getLogger(__name__)


def get_indicator_config(indicator_name: str):
    cfg = OmegaConf.load(DAGSTER_CONFIG)
    return cfg.assets.config.get(f"{indicator_name.lower()}_indicator", {})


def create_indicator_asset(indicator_name: str):
    """Factory function to create indicator assets."""

    @asset(
        name=f"{indicator_name.lower()}_indicator",
        description=f"Calculate {indicator_name} for all symbols",
        group_name="stock_indicators",
        ins={"price_ingestion": AssetIn("price_ingestion")}
    )
    def indicator_asset(price_ingestion):
        try:
            from app.celery_framework_app import app as celery_app
            cfg = get_indicator_config(indicator_name)  

            timeout = cfg.get("timeout", 600)
            task_name = cfg.get("celery_task", "tasks.calculate_store_indicators")


            results = price_ingestion["results"]
            symbols = [r["symbol"] for r in results if r["status"] == "success"]
            source = price_ingestion["source"]

            if not symbols:
                logger.warning(f"No symbols for {indicator_name}")
                return {"indicator": indicator_name, "status": "no_data", "results": []}

            logger.info(f"Submitting {indicator_name} tasks to Celery for {len(symbols)} symbols")

            tasks = []
            for symbol in symbols:
                try:   
                    task = celery_app.send_task(
                        task_name,
                        kwargs={
                            "symbol": symbol,
                            "indicator_name": indicator_name,
                            "source": source
                        }
                    )
                    tasks.append((symbol, task))
                except Exception as e:
                    logger.error(f"Failed submitting {symbol}: {str(e)}", exc_info=True)

            indicator_results = []

            for symbol, task in tasks:
                try:
                    result = task.get(timeout=timeout)
                    indicator_results.append(result)
                except Exception as e:
                    indicator_results.append({
                        "symbol": symbol,
                        "indicator": indicator_name,
                        "source": source,
                        "status": "error",
                        "error": str(e)
                    })

            successful = sum(1 for r in indicator_results if r.get("status") == "success")
            if successful == 0:
                raise Failure(f"{indicator_name}: No indicators were stored for ANY symbol.")

            # Fail if any task returned success but stored zero rows
            zero_row_failures = [
                r for r in indicator_results
                if r.get("status") == "success" and r.get("rows", 0) == 0
            ]
            if zero_row_failures:
                raise Failure(
                    f"{indicator_name}: Some symbols computed successfully but stored 0 rows: "
                    f"{[r['symbol'] for r in zero_row_failures]}"
                )

            return {
                "indicator": indicator_name,
                "total_symbols": len(symbols),
                "successful": successful,
                "results": indicator_results
            }

        except Exception as e:
            logger.error(f"{indicator_name} pipeline failed: {str(e)}", exc_info=True)
            raise Failure(f"{indicator_name} pipeline failed: {str(e)}")

    return indicator_asset


# Create all indicators
atr_indicator = create_indicator_asset("ATR")
ema_indicator = create_indicator_asset("EMA")
sma_indicator = create_indicator_asset("SMA")
bollinger_indicator = create_indicator_asset("BOLLINGER")
macd_indicator = create_indicator_asset("MACD")
rsi_indicator = create_indicator_asset("RSI")
