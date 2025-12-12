"""AI Models package for CoinScribe."""

from importlib import import_module
from typing import Any

__all__ = ['AIIndexModel', 'AIIndexPredictor']


def __getattr__(name: str) -> Any:
    if name == 'AIIndexModel':
        module = import_module('.training.model_architecture', __name__)
        return getattr(module, name)
    if name == 'AIIndexPredictor':
        module = import_module('.inference.predictor', __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
