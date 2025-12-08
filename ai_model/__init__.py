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

from .models.inference.predictor import AIIndexPredictor
from .api.endpoints import create_app

__all__ = ['AIIndexPredictor', 'create_app']
