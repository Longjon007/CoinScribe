import pytest
import pandas as pd
import numpy as np
from ai_model.data.pipelines.preprocessor import DataPreprocessor

class TestDataPreprocessor:
    @pytest.fixture
    def config(self):
        return {
            'data': {
                'sequence_length': 10,
                'features': ['open', 'close', 'volume'],
                'target': 'index_value',
                'normalize': True
            }
        }

    @pytest.fixture
    def preprocessor(self, config):
        return DataPreprocessor(config)

    def test_select_features_success(self, preprocessor):
        df = pd.DataFrame({
            'Open': [1, 2, 3],
            'Close': [4, 5, 6],
            'Volume': [100, 200, 300],
            'Other': [0, 0, 0]
        })
        selected_df = preprocessor.select_features(df)
        assert list(selected_df.columns) == ['Open', 'Close', 'Volume']
        assert len(selected_df) == 3

    def test_select_features_no_valid_features(self, preprocessor):
        df = pd.DataFrame({
            'Wrong': [1, 2, 3],
            'AlsoWrong': [4, 5, 6]
        })
        with pytest.raises(ValueError, match="No valid features found in dataframe"):
            preprocessor.select_features(df)

    def test_select_features_empty_dataframe(self, preprocessor):
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="No valid features found in dataframe"):
            preprocessor.select_features(df)

    def test_select_features_technical_indicators(self, preprocessor):
        df = pd.DataFrame({
            'Open': [1, 2, 3],
            'MA_7': [1.1, 1.2, 1.3],
            'RSI': [50, 51, 52]
        })
        selected_df = preprocessor.select_features(df)
        # 'open' maps to 'Open', and MA_7, RSI should be picked up
        assert 'Open' in selected_df.columns
        assert 'MA_7' in selected_df.columns
        assert 'RSI' in selected_df.columns
        assert len(selected_df.columns) == 3

    def test_create_sequences(self, preprocessor):
        data = np.random.rand(100, 5)
        targets = np.random.rand(100)
        X, y = preprocessor.create_sequences(data, targets, sequence_length=10)

        assert X.shape == (90, 10, 5)
        assert y.shape == (90,)
        assert np.array_equal(X[0], data[0:10])
        assert y[0] == targets[10]

    def test_normalize_data(self, preprocessor):
        features = np.random.rand(10, 2)
        targets = np.random.rand(10)

        # Test with fit=True
        X_norm, y_norm = preprocessor.normalize_data(features, targets, fit=True)
        assert preprocessor.fitted is True
        assert X_norm.shape == features.shape
        assert y_norm.shape == targets.shape

        # Test with fit=False
        X_norm2, y_norm2 = preprocessor.normalize_data(features, targets, fit=False)
        assert X_norm2.shape == features.shape
