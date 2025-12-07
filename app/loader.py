# price_app/app/loader.py

from typing import Any, Callable, Optional
from omegaconf import OmegaConf


class AppLoader:
    """Generic lazy loader for framework apps"""
    
    def __init__(self, name: str, config_path: str, factory: Callable, **kwargs):
        self.name = name
        self.config_path = config_path
        self.factory = factory
        self.kwargs = kwargs
        self._instance = None
    
    @property
    def instance(self):
        """Lazy load instance"""
        if self._instance is None:
            self._load()
        return self._instance
    
    def _load(self):
        """Load the framework app"""
        if self.config_path:
            cfg = OmegaConf.load(self.config_path)
            self._instance = self.factory(cfg, **self.kwargs)
        else:
            self._instance = self.factory(**self.kwargs)
        print(f"{self.name} loaded")
    
    def __getattr__(self, name):
        """Proxy attribute access to instance"""
        return getattr(self.instance, name)
