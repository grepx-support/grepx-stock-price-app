"""Prefect connection."""

from grepx_connection_registry import ConnectionBase
from prefect_framework.prefect_app import PrefectApp
import os
from omegaconf import OmegaConf


class PrefectConnection(ConnectionBase):
    """Prefect connection for managing flows and tasks."""
    
    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
        self.prefect_app = None
        # Load Prefect-specific configuration
        self.prefect_config = self._load_prefect_config()
    
    def _load_prefect_config(self):
        """Load Prefect-specific configuration from prefect.yaml."""
        config_file = getattr(self.config, 'config_file', 'prefect.yaml')
        config_path = os.path.join(self.config_dir, config_file)
        if os.path.exists(config_path):
            return OmegaConf.load(config_path)
        return None
    
    def connect(self) -> None:
        """Initialize Prefect app and load flows/tasks."""
        if self._client is None:
            self.prefect_app = PrefectApp()
            # Load flows from the existing prefect_app module
            from prefect_app.prefect_app import load_prefect_flows
            flows = load_prefect_flows()
            for name, flow in flows.items():
                self.prefect_app.register_flow(name, flow)
            self._client = self.prefect_app
    
    def disconnect(self) -> None:
        """Clear Prefect app."""
        self._client = None
        self.prefect_app = None
    
    def get_flows(self):
        """Get all registered flows."""
        if not self.is_connected():
            self.connect()
        return {name: self.prefect_app.get_flow(name) for name in self.prefect_app.list_flows()}
    
    def get_flow(self, flow_name: str):
        """Get a specific flow by name."""
        if not self.is_connected():
            self.connect()
        return self.prefect_app.get_flow(flow_name)
    
    def get_tasks(self):
        """Get all registered tasks."""
        if not self.is_connected():
            self.connect()
        return {name: self.prefect_app.get_task(name) for name in self.prefect_app.list_tasks()}
    
    def get_task(self, task_name: str):
        """Get a specific task by name."""
        if not self.is_connected():
            self.connect()
        return self.prefect_app.get_task(task_name)