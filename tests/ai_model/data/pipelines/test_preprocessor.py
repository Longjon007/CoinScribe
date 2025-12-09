import pytest
import numpy as np
import pandas as pd
import os
from unittest.mock import MagicMock, patch, mock_open
from ai_model.data.pipelines.preprocessor import DataPreprocessor

class TestDataPreprocessor:
    @pytest.fixture
    def preprocessor(self, mock_config_dict):
        return DataPreprocessor(mock_config_dict)

    def test_select_features(self, preprocessor, sample_market_data):
        df = preprocessor.select_features(sample_market_data)

        # Check if mapped columns exist
        # Config has ['Close', 'Volume'] (case insensitive in config dict logic above? No, config dict has 'Close', 'Volume')
        # Wait, mock_config_dict['data']['features'] = ['Close', 'Volume']
        # But DataPreprocessor mapping keys are lowercase: 'close', 'volume'.
        # Let's check mock_config_dict fixture in conftest.
        # It has 'features': ['Close', 'Volume'].
        # The preprocessor mapping is:
        # 'close': 'Close', 'volume': 'Volume'
        # If config has 'Close', mapping.get('Close', 'Close') returns 'Close'.
        # If 'Close' in df.columns, it is added.

        assert 'Close' in df.columns
        assert 'Volume' in df.columns
        assert 'Open' not in df.columns # Not in config features

    def test_select_features_technical_indicators(self, preprocessor, sample_market_data):
        # Add technical indicators manually to sample data
        sample_market_data['MA_7'] = 1.0
        sample_market_data['RSI'] = 50.0

        df = preprocessor.select_features(sample_market_data)

        assert 'MA_7' in df.columns
        assert 'RSI' in df.columns

    def test_select_features_error(self, preprocessor):
        df = pd.DataFrame({'Dummy': [1, 2, 3]})
        with pytest.raises(ValueError, match="No valid features found"):
            preprocessor.select_features(df)

    def test_create_sequences(self, preprocessor):
        data = np.array([[i] for i in range(20)])
        targets = np.array([i for i in range(20)])

        seq_len = 5
        X, y = preprocessor.create_sequences(data, targets, sequence_length=seq_len)

        # Length should be len(data) - seq_len = 15
        assert len(X) == 15
        assert len(y) == 15
        # X[0] should be 0..4
        assert np.array_equal(X[0], [[0], [1], [2], [3], [4]])
        # y[0] should be target at index 5 => 5
        assert y[0] == 5

    def test_normalize_data(self, preprocessor):
        features = np.array([[[1.0], [2.0]], [[3.0], [4.0]]]) # shape (2, 2, 1)
        targets = np.array([10.0, 20.0])

        X_norm, y_norm = preprocessor.normalize_data(features, targets, fit=True)

        assert preprocessor.fitted
        assert np.abs(X_norm.mean()) < 1.0 # Standard scaled should be around 0
        assert 0 <= y_norm.min() and y_norm.max() <= 1.0 # MinMax scaled

    def test_normalize_data_not_fitted(self, preprocessor):
        features = np.random.rand(2, 5, 2)
        targets = np.random.rand(2)

        with pytest.raises(ValueError, match="Scaler not fitted"):
            preprocessor.normalize_data(features, targets, fit=False)

    def test_inverse_transform_targets(self, preprocessor):
        features = np.array([[[1.0], [2.0]], [[3.0], [4.0]]])
        targets = np.array([10.0, 20.0])

        # Fit first
        _, y_norm = preprocessor.normalize_data(features, targets, fit=True)

        # Inverse
        y_orig = preprocessor.inverse_transform_targets(y_norm)

        assert np.allclose(y_orig, targets)

    def test_create_synthetic_targets(self, preprocessor, sample_market_data):
        targets = preprocessor.create_synthetic_targets(sample_market_data)
        assert len(targets) == len(sample_market_data)
        assert isinstance(targets, np.ndarray)

    def test_prepare_data(self, preprocessor, sample_market_data):
        # Ensure sufficient data length for sequence=10 + validation
        # sample_market_data is 100 rows. seq=10.

        (X_train, y_train), (X_val, y_val) = preprocessor.prepare_data(sample_market_data, validation_split=0.2)

        assert X_train.shape[1] == 10 # sequence length
        assert y_train.shape[1] == 10 # 10 output indices (hardcoded in preprocessor)
        assert len(X_val) > 0

    def test_save_load_scalers(self, preprocessor, tmp_path):
        # Fit first
        features = np.random.rand(10, 5, 2)
        targets = np.random.rand(10)
        preprocessor.normalize_data(features, targets, fit=True)

        filepath = tmp_path / "scalers.pkl"
        preprocessor.save_scalers(str(filepath))

        assert os.path.exists(filepath)

        # Create new preprocessor
        new_preprocessor = DataPreprocessor(preprocessor.config)
        assert not new_preprocessor.fitted

        new_preprocessor.load_scalers(str(filepath))
        assert new_preprocessor.fitted

    def test_save_scalers_error(self, preprocessor):
        with pytest.raises(ValueError, match="Scalers not fitted"):
            preprocessor.save_scalers("dummy.pkl")
