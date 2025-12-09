import pytest
import numpy as np
import os
from unittest.mock import MagicMock, patch
from ai_model.utils.visualization import plot_training_history, plot_predictions, plot_indices_comparison

class TestVisualization:
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_training_history(self, mock_savefig, mock_show, tmp_path):
        train_losses = [0.5, 0.4, 0.3]
        val_losses = [0.6, 0.5, 0.4]
        save_path = tmp_path / "loss.png"

        plot_training_history(train_losses, val_losses, save_path=str(save_path), show=True)

        mock_savefig.assert_called_once()
        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_training_history_no_show(self, mock_show):
        train_losses = [0.5]
        val_losses = [0.6]

        plot_training_history(train_losses, val_losses, show=False)

        mock_show.assert_not_called()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_predictions(self, mock_savefig, mock_show, tmp_path):
        actual = np.array([1, 2, 3])
        predicted = np.array([1.1, 1.9, 3.1])
        save_path = tmp_path / "pred.png"

        plot_predictions(actual, predicted, save_path=str(save_path))

        mock_savefig.assert_called_once()
        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_predictions_2d(self, mock_show):
        # Test with 2D arrays (should flatten)
        actual = np.array([[1], [2]])
        predicted = np.array([[1.1], [1.9]])

        plot_predictions(actual, predicted, show=True)

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_indices_comparison(self, mock_savefig, mock_show, tmp_path):
        data = {
            'Index1': [1, 2, 3],
            'Index2': [2, 3, 4]
        }
        save_path = tmp_path / "indices.png"

        plot_indices_comparison(data, save_path=str(save_path))

        mock_savefig.assert_called_once()
        mock_show.assert_called_once()
