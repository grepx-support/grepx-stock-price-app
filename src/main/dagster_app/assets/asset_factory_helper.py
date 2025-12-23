# dagster_app/assets/asset_factory_helper.py
from dagster_app.assets.base_assets import AssetFactory
from servers.factors.config import cfg


def create_asset_type(
    asset_type: str,
    group_name: str,
    fetch_task: str,
    store_task: str,
    store_indicators_task: str,
    globals_dict: dict,
):
    # Config assets
    globals_dict[f"config_prices_{asset_type}"] = (
        AssetFactory.create_prices_config_asset(asset_type, group_name)
    )

    globals_dict[f"config_indicators_{asset_type}"] = (
        AssetFactory.create_indicators_config_asset(asset_type, group_name)
    )

    # Fetch
    globals_dict[f"fetch_{asset_type}"] = (
        AssetFactory.create_fetch_asset(asset_type, fetch_task, group_name)
    )

    # Store prices
    globals_dict[f"store_{asset_type}"] = (
        AssetFactory.create_store_asset(asset_type, store_task, group_name)
    )

    # Indicators
    for indicator_name in cfg.indicators.keys():
        globals_dict[f"{asset_type}_{indicator_name.lower()}_indicator"] = (
            AssetFactory.create_indicator_asset(asset_type, indicator_name, group_name)
        )

    # Store indicators
    globals_dict[f"store_{asset_type}_indicators"] = (
        AssetFactory.create_store_indicators_asset(
            asset_type,
            store_indicators_task,
            group_name,
            list(cfg.indicators.keys()),
        )
    )


