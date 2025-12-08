"""Training module for AI models."""

__all__ = ['AIIndexModel', 'ModelTrainer']


def __getattr__(name):
    if name == 'AIIndexModel':
        from .model_architecture import AIIndexModel
        globals()[name] = AIIndexModel
        return AIIndexModel
    if name == 'ModelTrainer':
        from .trainer import ModelTrainer
        globals()[name] = ModelTrainer
        return ModelTrainer
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
