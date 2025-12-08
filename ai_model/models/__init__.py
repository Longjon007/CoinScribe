"""AI Models package for CoinScribe."""

__all__ = ['AIIndexModel', 'AIIndexPredictor']


def __getattr__(name):
    if name == 'AIIndexModel':
        from .training.model_architecture import AIIndexModel
        globals()[name] = AIIndexModel
        return AIIndexModel
    if name == 'AIIndexPredictor':
        from .inference.predictor import AIIndexPredictor
        globals()[name] = AIIndexPredictor
        return AIIndexPredictor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
