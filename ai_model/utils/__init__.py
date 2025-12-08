"""Utility modules for AI model."""

__all__ = ['setup_logger', 'plot_training_history', 'plot_predictions']


def __getattr__(name):
    if name == 'setup_logger':
        from .logger import setup_logger
        globals()[name] = setup_logger
        return setup_logger
    if name in {'plot_training_history', 'plot_predictions'}:
        from .visualization import plot_training_history, plot_predictions
        globals()['plot_training_history'] = plot_training_history
        globals()['plot_predictions'] = plot_predictions
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
