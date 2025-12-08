"""Data pipeline modules for loading and preprocessing."""

__all__ = ['MarketDataLoader', 'DataPreprocessor']


def __getattr__(name):
    if name == 'MarketDataLoader':
        from .data_loader import MarketDataLoader
        globals()[name] = MarketDataLoader
        return MarketDataLoader
    if name == 'DataPreprocessor':
        from .preprocessor import DataPreprocessor
        globals()[name] = DataPreprocessor
        return DataPreprocessor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
