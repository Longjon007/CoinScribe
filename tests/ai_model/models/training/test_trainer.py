import pytest
import torch
from unittest.mock import MagicMock, patch
from ai_model.models.training.trainer import ModelTrainer

class TestModelTrainer:
    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        model.return_value = (torch.randn(4, 5, requires_grad=True), None)
        model.parameters.return_value = iter([torch.randn(1, requires_grad=True)])
        model.state_dict.return_value = {}
        model.to.return_value = model
        return model

    @pytest.fixture
    def trainer(self, mock_model, mock_config_dict):
        # Increase patience for testing periodic checkpoints
        mock_config_dict['training']['early_stopping_patience'] = 20
        trainer = ModelTrainer(mock_model, mock_config_dict['training'])
        # Mock checkpoint dir to avoid filesystem writes
        trainer.checkpoint_dir = MagicMock()
        return trainer

    def test_init(self, trainer, mock_model):
        assert trainer.model == mock_model
        assert trainer.optimizer is not None
        assert trainer.scheduler is not None

    def test_init_with_device(self, mock_model, mock_config_dict):
        trainer = ModelTrainer(mock_model, mock_config_dict['training'], device='cpu')
        assert str(trainer.device) == 'cpu'

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
        assert mock_save_history.called

    @patch('ai_model.models.training.trainer.ModelTrainer.save_checkpoint')
    @patch('ai_model.models.training.trainer.ModelTrainer.save_training_history')
    def test_train_loop_periodic_checkpoint(self, mock_save_history, mock_save_checkpoint, trainer):
        # Test 11 epochs to trigger periodic checkpoint at epoch 10
        # Ensure patience is high enough
        trainer.config['early_stopping_patience'] = 20

        X_train = torch.randn(8, 10, 10).numpy()
        y_train = torch.randn(8, 5).numpy()
        X_val = torch.randn(4, 10, 10).numpy()
        y_val = torch.randn(4, 5).numpy()

        trainer.train(
            (X_train, y_train),
            (X_val, y_val),
            epochs=11,
            batch_size=4
        )

        # We check if mock_save_checkpoint called with periodic name
        call_args = [args[0] for args, _ in mock_save_checkpoint.call_args_list]
        assert any("checkpoint_epoch_10.pth" in str(arg) for arg in call_args)

    @patch('ai_model.models.training.trainer.ModelTrainer.save_checkpoint')
    @patch('ai_model.models.training.trainer.ModelTrainer.save_training_history')
    def test_early_stopping(self, mock_save_history, mock_save_checkpoint, trainer):
        X_train = torch.randn(8, 10, 10).numpy()
        y_train = torch.randn(8, 5).numpy()
        X_val = torch.randn(4, 10, 10).numpy()
        y_val = torch.randn(4, 5).numpy()

        # Set patience to 1
        trainer.config['early_stopping_patience'] = 1

        # Mock validate to return increasing loss
        with patch.object(trainer, 'validate', side_effect=[0.1, 0.2, 0.3]):
            trainer.train(
                (X_train, y_train),
                (X_val, y_val),
                epochs=10,
                batch_size=4
            )

            assert len(trainer.train_losses) == 2

    def test_load_checkpoint(self, trainer, tmp_path):
        # Create a dummy checkpoint
        checkpoint_path = tmp_path / "ckpt.pth"

        torch.save({
            'epoch': 5,
            'model_state_dict': {},
            'optimizer_state_dict': {'param_groups': []}, # Minimal valid dict for optimizer
            'scheduler_state_dict': {},
            'train_losses': [],
            'val_losses': [],
            'best_loss': 0.1
        }, checkpoint_path)

        trainer.checkpoint_dir = tmp_path

        # Mock load_state_dict calls
        trainer.optimizer.load_state_dict = MagicMock()
        trainer.scheduler.load_state_dict = MagicMock()

        trainer.load_checkpoint("ckpt.pth")

        assert trainer.epoch == 5
        assert trainer.best_loss == 0.1

    def test_load_checkpoint_file_not_found(self, trainer, tmp_path):
        trainer.checkpoint_dir = tmp_path
        with pytest.raises(FileNotFoundError):
            trainer.load_checkpoint("non_existent.pth")

    def test_save_training_history(self, trainer, tmp_path):
        # We need to use real filesystem to test saving
        trainer.checkpoint_dir = tmp_path
        trainer.train_losses = [0.5, 0.4]
        trainer.val_losses = [0.6, 0.5]
        trainer.best_loss = 0.5
        trainer.epoch = 1

        trainer.save_training_history()

        history_path = tmp_path / 'training_history.json'
        assert history_path.exists()
        import json
        with open(history_path, 'r') as f:
            data = json.load(f)
            assert data['train_losses'] == [0.5, 0.4]
