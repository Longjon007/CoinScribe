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

__version__ = "0.1.0"
__author__ = "CoinScribe Team"

__all__ = ['AIIndexPredictor', 'create_app']


def __getattr__(name):
    """
    Lazily import heavy submodules only when needed.
    
    Importing torch/yfinance is expensive and breaks lightweight tooling
    (e.g. docs tests) when those deps are unavailable.  Avoid importing
    them at module import time and defer until the attribute is accessed.
    """
    if name == 'AIIndexPredictor':
        from .models.inference.predictor import AIIndexPredictor
        globals()[name] = AIIndexPredictor
        return AIIndexPredictor
    
    if name == 'create_app':
        from .api.endpoints import create_app
        globals()[name] = create_app
        return create_app
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
