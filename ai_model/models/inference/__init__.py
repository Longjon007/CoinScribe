"""Inference module for AI models."""

__all__ = ['AIIndexPredictor']


def __getattr__(name):
    if name == 'AIIndexPredictor':
        from .predictor import AIIndexPredictor
        globals()[name] = AIIndexPredictor
        return AIIndexPredictor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
