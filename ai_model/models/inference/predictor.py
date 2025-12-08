"""
AI Index Predictor
===================

Handles inference and prediction using trained AI models.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

try:
    import torch  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - handled gracefully
    torch = None  # type: ignore
    _TORCH_IMPORT_ERROR = exc
else:  # pragma: no cover - import success path
    _TORCH_IMPORT_ERROR = None

from ...data.pipelines.preprocessor import DataPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIIndexPredictor:
    """Predictor class for generating AI investment indices."""
    
    def __init__(
        self,
        model_path: str,
        config: Dict,
        device: str = None
    ):
        """
        Initialize the predictor.
        
        Args:
            model_path: Path to trained model checkpoint
            config: Model configuration
            device: Device to run inference on
        """
        if torch is None:
            raise ImportError(
                "PyTorch is required for AIIndexPredictor but is not installed. "
                "Install it by running `pip install torch --index-url "
                "https://download.pytorch.org/whl/cpu`."
            ) from _TORCH_IMPORT_ERROR

        self.config = config
        self.model_path = Path(model_path)
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # Initialize model
        self.model = self._load_model()
        self.model.eval()
        
        # Initialize preprocessor
        self.preprocessor = DataPreprocessor(config)
        
        logger.info(f"Predictor initialized on {self.device}")
    
    def _load_model(self):
        """
        Load trained model from checkpoint.
        
        Returns:
            Loaded model
        """
        from ..training.model_architecture import AIIndexModel
        if not self.model_path.exists():
            logger.warning(f"Model checkpoint not found at {self.model_path}")
            logger.warning("Initializing new model (untrained)")
            
            # Initialize new model with config
            model = AIIndexModel(
                input_features=self.config.get('model', {}).get('input_features', 32),
                hidden_size=self.config.get('model', {}).get('hidden_size', 128),
                num_layers=self.config.get('model', {}).get('num_layers', 2),
                output_size=self.config.get('model', {}).get('output_size', 10),
                dropout=self.config.get('model', {}).get('dropout', 0.2)
            )
        else:
            logger.info(f"Loading model from {self.model_path}")
            
            # Load checkpoint
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            # Initialize model
            model = AIIndexModel(
                input_features=self.config.get('model', {}).get('input_features', 32),
                hidden_size=self.config.get('model', {}).get('hidden_size', 128),
                num_layers=self.config.get('model', {}).get('num_layers', 2),
                output_size=self.config.get('model', {}).get('output_size', 10),
                dropout=self.config.get('model', {}).get('dropout', 0.2)
            )
            
            # Load weights
            model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Loaded model from epoch {checkpoint.get('epoch', 'unknown')}")
        
        model.to(self.device)
        return model
    
    def predict(
        self,
        input_data: np.ndarray
    ) -> np.ndarray:
        """
        Make predictions on input data.
        
        Args:
            input_data: Input array of shape (batch_size, sequence_length, features)
            
        Returns:
            Predicted indices array
        """
        self.model.eval()
        
        # Convert to tensor
        input_tensor = torch.FloatTensor(input_data).to(self.device)
        
        # Make prediction
        with torch.no_grad():
            predictions, _ = self.model(input_tensor)
        
        # Convert back to numpy
        predictions_np = predictions.cpu().numpy()
        
        return predictions_np
    
    def predict_from_dataframe(
        self,
        df,
        sequence_length: int = None
    ) -> Dict[str, any]:
        """
        Make predictions from a pandas DataFrame.
        
        Args:
            df: DataFrame with market data
            sequence_length: Length of sequence to use
            
        Returns:
            Dictionary with predictions and metadata
        """
        sequence_length = sequence_length or self.preprocessor.sequence_length
        
        # Select and prepare features
        feature_df = self.preprocessor.select_features(df)
        features = feature_df.values
        
        # Take the last sequence
        if len(features) < sequence_length:
            raise ValueError(
                f"Not enough data points. Need at least {sequence_length}, got {len(features)}"
            )
        
        last_sequence = features[-sequence_length:]
        
        # Normalize if needed
        if self.preprocessor.normalize and self.preprocessor.fitted:
            last_sequence = self.preprocessor.feature_scaler.transform(last_sequence)
        
        # Add batch dimension
        input_data = last_sequence.reshape(1, sequence_length, -1)
        
        # Make prediction
        predictions = self.predict(input_data)
        
        # Format output
        timestamp = self._extract_timestamp(df)

        result = {
            'indices': predictions[0].tolist(),
            'index_names': [f"Index_{i+1}" for i in range(len(predictions[0]))],
            'confidence': self._calculate_confidence(predictions[0]),
            'timestamp': timestamp
        }
        
        return result
    
    def predict_next_indices(
        self,
        symbols: List[str],
        data_loader
    ) -> Dict[str, any]:
        """
        Predict indices for the next time step based on latest market data.
        
        Args:
            symbols: List of symbols to fetch data for
            data_loader: MarketDataLoader instance
            
        Returns:
            Dictionary with predictions
        """
        # Fetch latest data
        df = data_loader.prepare_training_data(symbols=symbols)
        
        if df.empty:
            raise ValueError("No data available for prediction")
        
        # Make prediction
        result = self.predict_from_dataframe(df)
        
        # Add additional context
        result['symbols'] = symbols
        result['model_path'] = str(self.model_path)
        
        return result
    
    @staticmethod
    def _calculate_confidence(predictions: np.ndarray) -> float:
        """
        Calculate confidence score for predictions.
        
        Args:
            predictions: Prediction array
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence calculation based on prediction variance
        # Lower variance = higher confidence
        variance = np.var(predictions)
        confidence = 1.0 / (1.0 + variance)
        
        return float(np.clip(confidence, 0, 1))

    def _extract_timestamp(self, df) -> Optional[str]:
        """
        Extract the most relevant timestamp value from the provided dataframe.
        Prefers explicit time columns and falls back to the dataframe index.
        """
        timestamp_columns = [
            'Datetime', 'datetime', 'Date', 'date',
            'timestamp', 'Timestamp'
        ]

        for column in timestamp_columns:
            if hasattr(df, 'columns') and column in df.columns:
                value = df[column].iloc[-1]
                formatted = self._format_timestamp(value)
                if formatted is not None:
                    return formatted

        if hasattr(df, 'index') and len(df.index) > 0:
            return self._format_timestamp(df.index[-1])

        return None

    @staticmethod
    def _format_timestamp(value) -> Optional[str]:
        """Format timestamp-like values consistently as ISO strings."""
        if value is None:
            return None

        if isinstance(value, np.datetime64):
            try:
                value = value.astype('datetime64[us]').tolist()
            except (TypeError, ValueError, OverflowError):
                return str(value)

        if hasattr(value, 'isoformat'):
            return value.isoformat()

        return str(value)
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_path': str(self.model_path),
            'device': str(self.device),
            'architecture': self.config.get('model', {}).get('architecture', 'lstm'),
            'input_features': self.config.get('model', {}).get('input_features', 32),
            'hidden_size': self.config.get('model', {}).get('hidden_size', 128),
            'num_layers': self.config.get('model', {}).get('num_layers', 2),
            'output_size': self.config.get('model', {}).get('output_size', 10),
            'model_exists': self.model_path.exists()
        }
