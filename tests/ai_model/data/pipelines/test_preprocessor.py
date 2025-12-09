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
        assert 'Close' in df.columns
        assert 'Volume' in df.columns

    def test_select_features_technical_indicators(self, preprocessor, sample_market_data):
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
        assert len(X) == 15
        assert len(y) == 15

    def test_normalize_data(self, preprocessor):
        features = np.array([[[1.0], [2.0]], [[3.0], [4.0]]])
        targets = np.array([10.0, 20.0])
        X_norm, y_norm = preprocessor.normalize_data(features, targets, fit=True)
        assert preprocessor.fitted

    def test_normalize_data_transform(self, preprocessor):
        # Cover the else branch (fit=False)
        features = np.array([[[1.0], [2.0]], [[3.0], [4.0]]])
        targets = np.array([10.0, 20.0])
        preprocessor.normalize_data(features, targets, fit=True)

        X_norm, y_norm = preprocessor.normalize_data(features, targets, fit=False)
        assert preprocessor.fitted

    def test_normalize_data_not_fitted(self, preprocessor):
        features = np.random.rand(2, 5, 2)
        targets = np.random.rand(2)
        with pytest.raises(ValueError, match="Scaler not fitted"):
            preprocessor.normalize_data(features, targets, fit=False)

    def test_normalize_data_no_normalize(self, preprocessor):
        preprocessor.normalize = False
        features = np.array([[[1.0]]])
        targets = np.array([10.0])
        X, y = preprocessor.normalize_data(features, targets, fit=True)
        assert np.array_equal(X, features)
        assert np.array_equal(y, targets)

    def test_inverse_transform_targets(self, preprocessor):
        features = np.array([[[1.0], [2.0]], [[3.0], [4.0]]])
        targets = np.array([10.0, 20.0])
        _, y_norm = preprocessor.normalize_data(features, targets, fit=True)
        y_orig = preprocessor.inverse_transform_targets(y_norm)
        assert np.allclose(y_orig, targets)

    def test_create_synthetic_targets(self, preprocessor, sample_market_data):
        # This covers default path with Close/Volume
        targets = preprocessor.create_synthetic_targets(sample_market_data)
        assert len(targets) == len(sample_market_data)

    def test_create_synthetic_targets_with_ma30(self, preprocessor, sample_market_data):
        # Cover branch where MA_30 exists
        sample_market_data['MA_30'] = sample_market_data['Close']
        targets = preprocessor.create_synthetic_targets(sample_market_data)
        assert len(targets) == len(sample_market_data)

    def test_create_synthetic_targets_fallback(self, preprocessor):
        # Cover branch where Close/Volume missing
        df = pd.DataFrame({'Dummy': [1, 2, 3]})
        targets = preprocessor.create_synthetic_targets(df)
        assert len(targets) == 3

    def test_prepare_data(self, preprocessor, sample_market_data):
        (X_train, y_train), (X_val, y_val) = preprocessor.prepare_data(sample_market_data, validation_split=0.2)
        assert X_train.shape[1] == 10
        assert len(X_val) > 0

    def test_save_load_scalers(self, preprocessor, tmp_path):
        features = np.random.rand(10, 5, 2)
        targets = np.random.rand(10)
        preprocessor.normalize_data(features, targets, fit=True)
        filepath = tmp_path / "scalers.pkl"
        preprocessor.save_scalers(str(filepath))
        assert os.path.exists(filepath)

        new_preprocessor = DataPreprocessor(preprocessor.config)
        new_preprocessor.load_scalers(str(filepath))
        assert new_preprocessor.fitted

    def test_save_scalers_error(self, preprocessor):
        with pytest.raises(ValueError, match="Scalers not fitted"):
            preprocessor.save_scalers("dummy.pkl")
