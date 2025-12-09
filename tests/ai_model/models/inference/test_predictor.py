import pytest
import pandas as pd
import numpy as np
import torch
from unittest.mock import MagicMock, patch
from ai_model.models.inference.predictor import AIIndexPredictor

class TestAIIndexPredictor:
    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        model.eval.return_value = None

        def forward_side_effect(x):
            batch_size = x.shape[0]
            output_size = 5
            return torch.rand(batch_size, output_size), None

        model.side_effect = forward_side_effect
        model.to.return_value = model
        return model

    @pytest.fixture
    def predictor(self, mock_config_dict, mock_model):
        with patch('ai_model.models.inference.predictor.AIIndexPredictor._load_model', return_value=mock_model):
            with patch('ai_model.models.inference.predictor.DataPreprocessor') as mock_preprocessor_cls:
                mock_preprocessor = MagicMock()
                mock_preprocessor.sequence_length = 10
                mock_preprocessor.normalize = True
                mock_preprocessor.fitted = True
                mock_preprocessor.feature_scaler.transform.side_effect = lambda x: x

                def select_features_side_effect(df):
                     return pd.DataFrame(
                         np.random.rand(len(df), 10),
                         index=df.index
                     )

                mock_preprocessor.select_features.side_effect = select_features_side_effect
                mock_preprocessor_cls.return_value = mock_preprocessor

                predictor = AIIndexPredictor(
                    model_path='dummy_path.pth',
                    config=mock_config_dict
                )
                return predictor

    def test_init_load_model_exists(self, mock_config_dict):
        # Test _load_model when file exists
        with patch('pathlib.Path.exists', return_value=True):
            with patch('torch.load') as mock_load:
                mock_load.return_value = {
                    'model_state_dict': {},
                    'epoch': 10
                }
                with patch('ai_model.models.inference.predictor.AIIndexModel') as mock_model_cls:
                    mock_model_instance = MagicMock()
                    mock_model_cls.return_value = mock_model_instance
                    predictor = AIIndexPredictor(
                        model_path='dummy_path.pth',
                        config=mock_config_dict
                    )
                    mock_model_instance.load_state_dict.assert_called()

    def test_init_load_model_not_exists(self, mock_config_dict):
        # Test _load_model when file does not exist (untrained)
        with patch('pathlib.Path.exists', return_value=False):
             with patch('ai_model.models.inference.predictor.AIIndexModel') as mock_model_cls:
                predictor = AIIndexPredictor(
                    model_path='dummy_path.pth',
                    config=mock_config_dict
                )
                mock_model_cls.assert_called()
                predictor.model.load_state_dict.assert_not_called()

    def test_init_with_device(self, mock_config_dict):
        # Test device initialization from string
        with patch('ai_model.models.inference.predictor.AIIndexPredictor._load_model'):
            with patch('ai_model.models.inference.predictor.DataPreprocessor'):
                predictor = AIIndexPredictor(
                    model_path='dummy.pth',
                    config=mock_config_dict,
                    device='cpu'
                )
                assert str(predictor.device) == 'cpu'

    def test_predict(self, predictor):
        input_data = np.random.rand(1, 10, 10)
        predictions = predictor.predict(input_data)
        assert isinstance(predictions, np.ndarray)
        assert predictions.shape == (1, 5)

    def test_predict_from_dataframe(self, predictor, sample_market_data):
        result = predictor.predict_from_dataframe(sample_market_data)
        assert 'indices' in result
        assert 'confidence' in result

    def test_predict_from_dataframe_insufficient_data(self, predictor):
        df = pd.DataFrame({'Close': [1, 2, 3]})
        with pytest.raises(ValueError):
            predictor.predict_from_dataframe(df)

    def test_predict_next_indices(self, predictor, sample_market_data):
        mock_loader = MagicMock()
        mock_loader.prepare_training_data.return_value = sample_market_data
        result = predictor.predict_next_indices(['BTC-USD'], mock_loader)
        assert 'indices' in result

    def test_predict_next_indices_empty(self, predictor):
        mock_loader = MagicMock()
        mock_loader.prepare_training_data.return_value = pd.DataFrame()
        with pytest.raises(ValueError):
            predictor.predict_next_indices(['BTC-USD'], mock_loader)

    def test_calculate_confidence(self):
        predictions = np.array([0.1, 0.2, 0.15, 0.18, 0.12])
        conf = AIIndexPredictor._calculate_confidence(predictions)
        assert 0 <= conf <= 1

    def test_get_model_info(self, predictor):
        info = predictor.get_model_info()
        assert info['model_path'] == 'dummy_path.pth'
