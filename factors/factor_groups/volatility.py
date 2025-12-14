from factors.indicators.atr import calculate_atr
from factors.indicators.bollinger import calculate_bollinger
from omegaconf import OmegaConf


cfg = OmegaConf.load("config/config.yaml")

def atr_factor(df):
    return {
        "atr_14": calculate_atr(df, cfg.indicators.ATR.period)
    }


def bollinger_factors(df):
    upper, middle, lower = calculate_bollinger(
        df,
        cfg.indicators.BOLLINGER.period,
        cfg.indicators.BOLLINGER.std_dev
    )
    return {
        "bb_upper": upper,
        "bb_middle": middle,
        "bb_lower": lower
    }
