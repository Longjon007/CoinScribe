import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from ai_model.config import Config

@pytest.fixture
def mock_config_dict():
    return {
        'model': {
            'architecture': 'lstm',
            'input_features': 10,
            'hidden_size': 32,
            'num_layers': 1,
            'output_size': 5,
            'dropout': 0.1
        },
        'training': {
            'batch_size': 4,
            'learning_rate': 0.001,
            'epochs': 2,
            'validation_split': 0.2,
            'early_stopping_patience': 2,
            'checkpoint_dir': 'tests/checkpoints'
        },
        'data': {
            'sequence_length': 10,
            'features': ['Close', 'Volume'],
            'target': 'index_value',
            'normalize': True
        },
        'api': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': True,
            'cors_origins': ['*']
        },
        'data_sources': {
            'market_data': {
                'provider': 'yfinance',
                'symbols': ['BTC-USD', 'ETH-USD'],
                'interval': '1h',
                'period': '1d'
            },
            'news_data': {
                'enabled': True,
                'sentiment_analysis': True
            }
        },
        'serving': {
            'model_path': 'tests/checkpoints/best_model.pth',
            'cache_predictions': True,
            'cache_ttl': 60
        }
    }

@pytest.fixture
def mock_config(mock_config_dict):
    config = MagicMock(spec=Config)
    config._config = mock_config_dict

    def get(key, default=None):
        keys = key.split('.')
        value = mock_config_dict
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    config.get.side_effect = get
    config.model = mock_config_dict['model']
    config.training = mock_config_dict['training']
    config.data = mock_config_dict['data']
    config.api = mock_config_dict['api']
    return config

@pytest.fixture
def sample_market_data():
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    data = {
        'Open': np.random.rand(100) * 100,
        'High': np.random.rand(100) * 105,
        'Low': np.random.rand(100) * 95,
        'Close': np.random.rand(100) * 100,
        'Volume': np.random.randint(1000, 10000, 100),
        'symbol': ['BTC-USD'] * 100
    }
    return pd.DataFrame(data, index=dates).reset_index().rename(columns={'index': 'Datetime'})
