"""Configuration schemas using dataclasses for type safety."""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AppMetadata:
    name: str
    version: str


@dataclass
class CeleryConfig:
    broker_url: str
    result_backend: str
    task_serializer: str
    result_serializer: str
    accept_content: List[str]
    timezone: str
    enable_utc: bool
    synchronous: bool


@dataclass
class WorkerConfig:
    pool: str
    max_concurrent: int
    worker_prefetch_multiplier: int
    worker_max_tasks_per_child: int


@dataclass
class TaskConfig:
    track_started: bool
    time_limit: int
    soft_time_limit: int
    task_compression: str
    task_ignore_result: bool
    autoretry_for: List[str]
    max_retries: int
    default_retry_delay: int


@dataclass
class TasksConfig:
    modules: List[str]
    directories: List[str]


@dataclass
class DatabaseConfig:
    connection_string: str


@dataclass
class AppConfig:
    app: AppMetadata
    celery: CeleryConfig
    worker: WorkerConfig
    task: TaskConfig
    tasks: TasksConfig
    database: DatabaseConfig


# Asset Config Schemas
@dataclass
class AssetTypeConfig:
    symbols: List[str]
    fetch_timeout: int
    store_timeout: int


@dataclass
class AssetTypesConfig:
    stocks: AssetTypeConfig
    indices: AssetTypeConfig
    futures: AssetTypeConfig


@dataclass
class IndicatorPeriods:
    periods: List[int]


@dataclass
class EMAConfig:
    periods: List[int]


@dataclass
class RSIConfig:
    period: int


@dataclass
class MACDConfig:
    fast: int
    slow: int
    signal: int


@dataclass
class BollingerConfig:
    period: int
    std_dev: int


@dataclass
class ATRConfig:
    period: int


@dataclass
class IndicatorsConfig:
    SMA: IndicatorPeriods
    EMA: EMAConfig
    RSI: RSIConfig
    MACD: MACDConfig
    BOLLINGER: BollingerConfig
    ATR: ATRConfig


@dataclass
class FactorsConfig:
    missing_value: Dict[str, Any]


@dataclass
class ColumnsConfig:
    high: str
    low: str
    close: str
    open: str
    volume: str


@dataclass
class NamingConventionConfig:
    case_mode: str
    separator: str
    price_template: str
    indicator_template: str


@dataclass
class AssetConfig:
    asset_types: AssetTypesConfig
    start_date: str
    end_date: str
    indicators: IndicatorsConfig
    factors: FactorsConfig
    columns: ColumnsConfig
    naming_convention: NamingConventionConfig


# Dagster Config Schemas
@dataclass
class DagsterAppConfig:
    name: str
    version: str


@dataclass
class DagsterMainConfig:
    module_name: str
    home: str


@dataclass
class AssetsModulesConfig:
    modules: List[str]
    directories: List[str]


@dataclass
class DagsterConfig:
    app: DagsterAppConfig
    dagster: DagsterMainConfig
    assets: AssetsModulesConfig
    jobs: List[Any]
    ops: Dict[str, List[Any]]
