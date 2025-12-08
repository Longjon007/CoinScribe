"""
Data Preprocessor
==================

Preprocesses and transforms market data for model training.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocesses market data for AI model training."""
    
    def __init__(self, config: Dict):
        """
        Initialize the preprocessor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.sequence_length = config.get('data', {}).get('sequence_length', 60)
        self.feature_columns = config.get('data', {}).get('features', [])
        self.target_column = config.get('data', {}).get('target', 'index_value')
        self.normalize = config.get('data', {}).get('normalize', True)
        
        self.feature_scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        self.fitted = False
    
    def select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select relevant features from dataframe.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with selected features
        """
        # Map config feature names to actual column names
        feature_mapping = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'market_cap': 'Close',  # Using close as proxy for now
            'sentiment_score': 'sentiment_score'
        }
        
        available_features = []
        for feature in self.feature_columns:
            col_name = feature_mapping.get(feature, feature)
            if col_name in df.columns:
                available_features.append(col_name)
            else:
                logger.warning(f"Feature '{feature}' (mapped to '{col_name}') not found in dataframe")
        
        # Add technical indicators if available
        technical_indicators = [
            'MA_7', 'MA_30', 'EMA_12', 'EMA_26', 
            'MACD', 'RSI', 'Volatility', 'Price_Change_Pct'
        ]
        
        for indicator in technical_indicators:
            if indicator in df.columns and indicator not in available_features:
                available_features.append(indicator)
        
        if not available_features:
            raise ValueError("No valid features found in dataframe")
        
        logger.info(f"Selected features: {available_features}")
        return df[available_features].copy()
    
    def create_sequences(
        self,
        data: np.ndarray,
        targets: np.ndarray,
        sequence_length: int = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time series prediction.
        
        Args:
            data: Feature data array
            targets: Target data array
            sequence_length: Length of sequences
            
        Returns:
            Tuple of (X, y) where X has shape (samples, sequence_length, features)
        """
        sequence_length = sequence_length or self.sequence_length
        
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            X.append(data[i:i + sequence_length])
            y.append(targets[i + sequence_length])
        
        return np.array(X), np.array(y)
    
    def normalize_data(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        fit: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalize features and targets.
        
        Args:
            features: Feature array
            targets: Target array
            fit: Whether to fit scalers (True for training, False for inference)
            
        Returns:
            Tuple of normalized (features, targets)
        """
        if not self.normalize:
            return features, targets
        
        # Reshape for scaling
        original_shape = features.shape
        features_2d = features.reshape(-1, features.shape[-1])
        
        if fit:
            features_normalized = self.feature_scaler.fit_transform(features_2d)
            targets_normalized = self.target_scaler.fit_transform(
                targets.reshape(-1, 1)
            ).flatten()
            self.fitted = True
        else:
            if not self.fitted:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            features_normalized = self.feature_scaler.transform(features_2d)
            targets_normalized = self.target_scaler.transform(
                targets.reshape(-1, 1)
            ).flatten()
        
        # Reshape back
        features_normalized = features_normalized.reshape(original_shape)
        
        return features_normalized, targets_normalized
    
    def inverse_transform_targets(self, targets: np.ndarray) -> np.ndarray:
        """
        Inverse transform normalized targets back to original scale.
        
        Args:
            targets: Normalized target array
            
        Returns:
            Original scale targets
        """
        if not self.normalize or not self.fitted:
            return targets
        
        return self.target_scaler.inverse_transform(
            targets.reshape(-1, 1)
        ).flatten()
    
    def create_synthetic_targets(self, df: pd.DataFrame) -> np.ndarray:
        """
        Create synthetic target indices for training.
        
        In production, this would use actual investment index data.
        For now, we create synthetic targets based on weighted market metrics.
        
        Args:
            df: DataFrame with market features
            
        Returns:
            Array of target index values
        """
        # Create a composite index based on price movements and volume
        # This is a simplified placeholder - real implementation would use actual indices
        
        if 'Close' in df.columns and 'Volume' in df.columns:
            # Normalize close and volume
            close_norm = (df['Close'] - df['Close'].min()) / (df['Close'].max() - df['Close'].min() + 1e-8)
            volume_norm = (df['Volume'] - df['Volume'].min()) / (df['Volume'].max() - df['Volume'].min() + 1e-8)
            
            # Combine with weights
            synthetic_index = 0.7 * close_norm + 0.3 * volume_norm
            
            # Add some market trend component
            if 'MA_30' in df.columns:
                trend = (df['Close'] - df['MA_30']) / (df['MA_30'] + 1e-8)
                trend_norm = (trend - trend.min()) / (trend.max() - trend.min() + 1e-8)
                synthetic_index = 0.6 * synthetic_index + 0.4 * trend_norm
            
            return synthetic_index.values
        else:
            # Fallback to random indices
            logger.warning("Using random targets - Close or Volume not found")
            return np.random.rand(len(df))
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        validation_split: float = 0.2
    ) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
        """
        Prepare complete dataset for training.
        
        Args:
            df: Input dataframe
            validation_split: Fraction of data to use for validation
            
        Returns:
            Tuple of ((X_train, y_train), (X_val, y_val))
        """
        # Select features
        feature_df = self.select_features(df)
        
        # Create synthetic targets
        targets = self.create_synthetic_targets(df)
        
        # Convert to numpy
        features = feature_df.values
        
        # Create sequences
        X, y = self.create_sequences(features, targets)
        
        logger.info(f"Created {len(X)} sequences with shape {X.shape}")
        
        # Split into train and validation
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Normalize
        X_train, y_train = self.normalize_data(X_train, y_train, fit=True)
        X_val, y_val = self.normalize_data(X_val, y_val, fit=False)
        
        # Reshape y to have proper dimensions for model
        y_train = np.tile(y_train.reshape(-1, 1), (1, 10))  # 10 output indices
        y_val = np.tile(y_val.reshape(-1, 1), (1, 10))
        
        logger.info(f"Training samples: {len(X_train)}, Validation samples: {len(X_val)}")
        
        return (X_train, y_train), (X_val, y_val)
    
    def save_scalers(self, filepath: str):
        """
        Save fitted scalers to file.
        
        Args:
            filepath: Path to save scalers
        """
        if not self.fitted:
            raise ValueError("Scalers not fitted yet")
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'feature_scaler': self.feature_scaler,
                'target_scaler': self.target_scaler
            }, f)
        
        logger.info(f"Saved scalers to {filepath}")
    
    def load_scalers(self, filepath: str):
        """
        Load fitted scalers from file.
        
        Args:
            filepath: Path to load scalers from
        """
        with open(filepath, 'rb') as f:
            scalers = pickle.load(f)
        
        self.feature_scaler = scalers['feature_scaler']
        self.target_scaler = scalers['target_scaler']
        self.fitted = True
        
        logger.info(f"Loaded scalers from {filepath}")
