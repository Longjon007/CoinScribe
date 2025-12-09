import pytest
import torch
from ai_model.models.training.model_architecture import AIIndexModel

class TestAIIndexModel:
    def test_initialization(self):
        model = AIIndexModel(
            input_features=10,
            hidden_size=32,
            num_layers=2,
            output_size=5,
            dropout=0.2
        )
        assert isinstance(model, AIIndexModel)
        assert model.hidden_size == 32
        assert model.num_layers == 2

    def test_forward_pass(self):
        batch_size = 4
        seq_length = 10
        input_features = 10
        output_size = 5

        model = AIIndexModel(
            input_features=input_features,
            hidden_size=32,
            num_layers=1,
            output_size=output_size
        )

        x = torch.randn(batch_size, seq_length, input_features)
        predictions, hidden = model(x)

        assert predictions.shape == (batch_size, output_size)
        assert isinstance(hidden, tuple)
        assert len(hidden) == 2  # h_0, c_0

    def test_predict_indices(self):
        model = AIIndexModel(input_features=10, output_size=5)
        x = torch.randn(1, 10, 10)
        predictions = model.predict_indices(x)
        assert predictions.shape == (1, 5)

    def test_initialization_defaults(self):
        model = AIIndexModel()
        assert model.hidden_size == 128
        assert model.num_layers == 2
