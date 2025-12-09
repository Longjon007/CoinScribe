import pytest
import torch
from unittest.mock import MagicMock, patch
from ai_model.models.training.trainer import ModelTrainer

class TestModelTrainer:
    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        # Mock forward pass
        # The output of the model needs to be connected to the graph for backward to work,
        # but since we are mocking the model, we can't easily rely on autograd unless the output comes from a tracked computation.
        # Alternatively, we can mock loss.backward() so it doesn't actually try to compute gradients.

        # However, trainer.train_epoch calls:
        # predictions, _ = self.model(data)
        # loss = self.criterion(predictions, target)
        # loss.backward()

        # If model is a Mock, predictions is a Mock or whatever we set return_value to.
        # If we return a tensor with requires_grad=True, loss will have grad_fn.

        model.return_value = (torch.randn(4, 5, requires_grad=True), None)
        model.parameters.return_value = iter([torch.randn(1, requires_grad=True)])
        model.state_dict.return_value = {}
        model.to.return_value = model
        return model

    @pytest.fixture
    def trainer(self, mock_model, mock_config_dict):
        trainer = ModelTrainer(mock_model, mock_config_dict['training'])
        # Mock checkpoint dir to avoid filesystem writes
        trainer.checkpoint_dir = MagicMock()
        return trainer

    def test_init(self, trainer, mock_model):
        assert trainer.model == mock_model
        assert trainer.optimizer is not None
        assert trainer.scheduler is not None

    def test_train_epoch(self, trainer):
        # Create a dummy dataloader
        loader = [(torch.randn(4, 10, 10), torch.randn(4, 5))]

        loss = trainer.train_epoch(loader)

        assert isinstance(loss, float)
        assert trainer.model.train.called

    def test_validate(self, trainer):
        loader = [(torch.randn(4, 10, 10), torch.randn(4, 5))]

        loss = trainer.validate(loader)

        assert isinstance(loss, float)
        assert trainer.model.eval.called

    @patch('ai_model.models.training.trainer.ModelTrainer.save_checkpoint')
    @patch('ai_model.models.training.trainer.ModelTrainer.save_training_history')
    def test_train_loop(self, mock_save_history, mock_save_checkpoint, trainer):
        # Mock data
        X_train = torch.randn(8, 10, 10).numpy()
        y_train = torch.randn(8, 5).numpy()
        X_val = torch.randn(4, 10, 10).numpy()
        y_val = torch.randn(4, 5).numpy()

        history = trainer.train(
            (X_train, y_train),
            (X_val, y_val),
            epochs=2,
            batch_size=4
        )

        assert 'train_losses' in history
        assert 'val_losses' in history
        assert len(history['train_losses']) == 2
        assert mock_save_checkpoint.called
