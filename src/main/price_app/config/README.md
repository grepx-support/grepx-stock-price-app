# Configuration Management with Hydra Core

## Overview

This configuration system uses Hydra Core to load YAML configurations with type safety through dataclasses.

## Structure

```
price_app/
├── src/
│   └── main/
│       ├── price_app/
│       │   └── config/
│       │       ├── __init__.py
│       │       ├── loader.py          # Main ConfigLoader
│       │       ├── schemas.py         # Dataclass schemas
│       │       ├── app_config.py      # App config loader
│       │       ├── asset_config.py    # Asset config loader
│       │       ├── dagster_config.py  # Dagster config loader
│       │       └── examples.py        # Usage examples
│       └── resources/
│           ├── app.yaml
│           ├── asset.yaml
│           └── dagster.yaml
```

## Usage

### 1. Basic Usage - Main ConfigLoader

```python
from price_app.config import ConfigLoader

loader = ConfigLoader()

# Load individual configs
app_cfg = loader.load_app_config()
asset_cfg = loader.load_asset_config()
dagster_cfg = loader.load_dagster_config()

# Or load all at once
app_cfg, asset_cfg, dagster_cfg = loader.load_all()

# Access values
print(app_cfg.celery.broker_url)
print(asset_cfg.asset_types.stocks.symbols)

loader.cleanup()
```

### 2. Dedicated Loaders (Recommended)

```python
from price_app.config import AppConfigLoader, AssetConfigLoader, DagsterConfigLoader

# App configuration
app_loader = AppConfigLoader()
print(app_loader.celery_config.broker_url)
print(app_loader.database_config.connection_string)
print(app_loader.task_modules)

# Asset configuration
asset_loader = AssetConfigLoader()
print(asset_loader.stock_symbols)
print(asset_loader.all_symbols)
print(asset_loader.indicators.SMA.periods)

# Dagster configuration
dagster_loader = DagsterConfigLoader()
print(dagster_loader.module_name)
print(dagster_loader.asset_modules)
```

### 3. Singleton Pattern

```python
from price_app.config import AppConfigLoader

# Create once at application startup
app_config = AppConfigLoader()


# Use throughout your application
def some_function():
    broker_url = app_config.celery_config.broker_url
    # ... use config
```

### 4. Raw Config Access

```python
from price_app.config import ConfigLoader

loader = ConfigLoader()

# Load as DictConfig (no type conversion)
raw_cfg = loader.load_raw("app")
print(raw_cfg.celery.timezone)

# Override values
overrides = {"worker.max_concurrent": 10}
modified = loader.override_config(raw_cfg, overrides)

loader.cleanup()
```

## Benefits

1. **Type Safety**: Dataclass schemas provide IDE autocomplete and type checking
2. **Organized**: Separate loaders for each config type
3. **Flexible**: Can use typed or raw configs as needed
4. **Cached**: Configs are loaded once and cached
5. **Reloadable**: Can force reload with `.reload()` method
6. **Hydra Power**: Supports all Hydra features (overrides, composition, etc.)

## Configuration Files

### app.yaml

- Application metadata
- Celery configuration
- Worker settings
- Task configuration
- Database connection

### asset.yaml

- Asset types (stocks, indices, futures)
- Indicators (SMA, EMA, RSI, MACD, etc.)
- Date ranges
- Column mappings
- Naming conventions

### dagster.yaml

- Dagster module configuration
- Asset modules
- Jobs and ops

## Examples

Run the examples:

```python
python - m
price_app.config.examples
```

## Installation

Requires:

```
hydra-core>=1.3.0
omegaconf>=2.3.0
```
