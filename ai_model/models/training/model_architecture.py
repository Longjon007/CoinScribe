"""
AI Index Model Architecture
============================

This module defines the neural network architecture for predicting
investment indices based on historical market data and news sentiment.
"""

import torch
import torch.nn as nn
from typing import Tuple


class AIIndexModel(nn.Module):
    """
    LSTM-based model for predicting AI investment indices.
    
    This model processes time-series market data and news sentiment
    to generate predictions for investment indices.
    """
    
    def __init__(
        self,
        input_features: int = 32,
        hidden_size: int = 128,
        num_layers: int = 2,
        output_size: int = 10,
        dropout: float = 0.2
    ):
        """
        Initialize the AI Index Model.
        
        Args:
            input_features: Number of input features per time step
            hidden_size: Number of features in the hidden state
            num_layers: Number of LSTM layers
            output_size: Number of output indices
            dropout: Dropout probability
        """
        super(AIIndexModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer for temporal sequence processing
        self.lstm = nn.LSTM(
            input_size=input_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism for focusing on important time steps
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=4,
            dropout=dropout,
            batch_first=True
        )
        
        # Fully connected layers for index prediction
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, output_size)
        )
        
        # Batch normalization
        self.batch_norm = nn.BatchNorm1d(hidden_size)
        
    def forward(
        self,
        x: torch.Tensor,
        hidden: Tuple[torch.Tensor, torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass through the model.
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_features)
            hidden: Optional hidden state tuple (h_0, c_0)
            
        Returns:
            Tuple of (predictions, hidden_state)
            - predictions: Tensor of shape (batch_size, output_size)
            - hidden_state: Tuple of hidden and cell states
        """
        batch_size = x.size(0)
        
        # Initialize hidden state if not provided
        if hidden is None:
            hidden = self._init_hidden(batch_size, x.device)
        
        # LSTM processing
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Apply attention mechanism
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use the last time step output
        last_output = attn_out[:, -1, :]
        
        # Apply batch normalization
        normalized = self.batch_norm(last_output)
        
        # Generate predictions
        predictions = self.fc_layers(normalized)
        
        return predictions, hidden
    
    def _init_hidden(
        self,
        batch_size: int,
        device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Initialize hidden state for LSTM.
        
        Args:
            batch_size: Batch size
            device: Device to create tensors on
            
        Returns:
            Tuple of (h_0, c_0) initialized to zeros
        """
        h_0 = torch.zeros(
            self.num_layers,
            batch_size,
            self.hidden_size
        ).to(device)
        
        c_0 = torch.zeros(
            self.num_layers,
            batch_size,
            self.hidden_size
        ).to(device)
        
        return (h_0, c_0)
    
    def predict_indices(self, x: torch.Tensor) -> torch.Tensor:
        """
        Convenience method for making predictions.
        
        Args:
            x: Input tensor
            
        Returns:
            Predicted indices
        """
        self.eval()
        with torch.no_grad():
            predictions, _ = self.forward(x)
        return predictions
