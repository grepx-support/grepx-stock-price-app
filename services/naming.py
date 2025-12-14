from omegaconf import OmegaConf
import logging

logger = logging.getLogger(__name__)

class NamingConvention:
    """Handle collection naming with configurable patterns"""
    
    def __init__(self):
        self.cfg = OmegaConf.load("config/config.yaml")
        self.naming_cfg = self.cfg.naming_convention
    
    def _apply_case(self, value: str, case_mode: str) -> str:
        """Apply case conversion based on mode"""
        if case_mode == "lower":
            return value.lower()
        elif case_mode == "upper":
            return value.upper()
        elif case_mode == "mixed":
            return value.capitalize()
        else:  # "original"
            return value
    
    def get_price_collection_name(self, symbol: str) -> str:
        """Generate collection name for price data"""
        case_mode = self.naming_cfg.case_mode
        separator = self.naming_cfg.separator
        template = self.naming_cfg.price_template
        
        # Apply case to symbol and separator
        symbol = self._apply_case(symbol, case_mode)
        
        # Build collection name
        collection_name = template.format(
            symbol=symbol,
            sep=separator
        )
        
        logger.info(f"Generated price collection: {collection_name}")
        return collection_name
    
    def get_indicator_collection_name(self, symbol: str, factor: str) -> str:
        """Generate collection name for indicator data"""
        case_mode = self.naming_cfg.case_mode
        separator = self.naming_cfg.separator
        template = self.naming_cfg.indicator_template
        
        # Apply case to symbol and factor
        symbol = self._apply_case(symbol, case_mode)
        factor = self._apply_case(factor, case_mode)
        
        # Build collection name
        collection_name = template.format(
            symbol=symbol,
            factor=factor,
            sep=separator
        )
        
        logger.info(f"Generated indicator collection: {collection_name}")
        return collection_name

# Singleton instance
naming = NamingConvention()