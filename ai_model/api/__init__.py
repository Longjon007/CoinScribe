"""API module for AI model serving."""

__all__ = ['create_app']


def __getattr__(name):
    if name == 'create_app':
        from .endpoints import create_app
        globals()[name] = create_app
        return create_app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
