"""AI Models package for CoinScribe."""

from .training.model_architecture import AIIndexModel
from .inference.predictor import AIIndexPredictor

__all__ = ['AIIndexModel', 'AIIndexPredictor']
