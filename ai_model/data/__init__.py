"""Data processing and pipeline modules."""

__all__ = ['MarketDataLoader', 'DataPreprocessor']


def __getattr__(name):
    if name == 'MarketDataLoader':
        from .pipelines.data_loader import MarketDataLoader
        globals()[name] = MarketDataLoader
        return MarketDataLoader
    if name == 'DataPreprocessor':
        from .pipelines.preprocessor import DataPreprocessor
        globals()[name] = DataPreprocessor
        return DataPreprocessor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
