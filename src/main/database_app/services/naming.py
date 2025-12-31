# services/naming.py  (or wherever NamingConvention lives)

from omegaconf import OmegaConf
from servers.factors.config import cfg


class NamingConvention:
    """Handle naming with configurable patterns and DB routing"""
    def __init__(self):
        self.cfg = cfg
        self.naming_cfg = self.cfg.naming_convention

    def _apply_case(self, value: str, case_mode: str) -> str:
        if case_mode == "lower":
            return value.lower()
        elif case_mode == "upper":
            return value.upper()
        elif case_mode == "mixed":
            return value.capitalize()
        else:
            return value

    def get_analysis_db_name(self, asset_type: str) -> str:
        """Get database name for asset type from asset.yaml database_naming config."""
        from servers.app import Application

        if not asset_type or asset_type.strip() == "":
            raise ValueError("asset_type cannot be empty or None")

        app = Application()
        asset_type = asset_type.lower().strip()

        # Try to get from asset.yaml database_naming section
        if hasattr(app.config, 'database_naming'):
            db_name = app.config.database_naming.get(asset_type)
            if db_name:
                db_name_str = str(db_name).strip()
                if db_name_str:
                    return db_name_str

        # Fallback to hardcoded mapping
        db_map = {
            "stocks": "stocks_analysis",
            "indices": "indices_analysis",
            "futures": "futures_analysis",
        }
        db_name = db_map.get(asset_type)
        if not db_name or db_name.strip() == "":
            raise ValueError(f"Unknown or empty database name for asset_type: {asset_type}")
        return db_name

    def get_price_collection_name(self, asset_type: str, symbol: str) -> str:
        case_mode = self.naming_cfg.case_mode
        separator = self.naming_cfg.separator
        template = self.naming_cfg.price_template  # e.g., "{symbol}{sep}prices"

        symbol = self._apply_case(symbol, case_mode)
        collection_name = template.format(symbol=symbol, sep=separator)
        return collection_name

    def get_indicator_collection_name(self, asset_type: str, symbol: str, factor: str) -> str:
        case_mode = self.naming_cfg.case_mode
        separator = self.naming_cfg.separator
        template = self.naming_cfg.indicator_template  # e.g., "{symbol}{sep}{factor}"

        symbol = self._apply_case(symbol, case_mode)
        factor = self._apply_case(factor, case_mode)
        collection_name = template.format(symbol=symbol, factor=factor, sep=separator)
        return collection_name

# Singleton
naming = NamingConvention()