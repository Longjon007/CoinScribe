"""
CoinScribe AI Model Package
============================

This package provides AI/ML capabilities for the CoinScribe platform,
specifically for the "Invest & Trade's AI Index" creation feature.

The package includes:
- Model training pipelines
- Data processing utilities
- API endpoints for model inference
- Configuration management
"""

from importlib import import_module
from typing import Any

__version__ = "0.1.0"
__author__ = "CoinScribe Team"

__all__ = ['AIIndexPredictor', 'create_app']


def __getattr__(name: str) -> Any:
    if name == 'AIIndexPredictor':
        module = import_module('.models.inference.predictor', __name__)
        return getattr(module, name)
    if name == 'create_app':
        module = import_module('.api.endpoints', __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
