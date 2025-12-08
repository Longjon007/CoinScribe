#!/usr/bin/env python3
"""
Training Script for CoinScribe AI Model
========================================

This script trains the AI model for generating investment indices.

Usage:
    python train_model.py
    python train_model.py --epochs 50 --batch-size 64
"""

import argparse
import sys
from pathlib import Path

# Add ai_model to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_model.config import config
from ai_model.models.training.model_architecture import AIIndexModel
from ai_model.models.training.trainer import ModelTrainer
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.data.pipelines.preprocessor import DataPreprocessor
from ai_model.utils.logger import setup_logger
from ai_model.utils.visualization import plot_training_history


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Train CoinScribe AI Index Model'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Number of training epochs (default: from config)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Batch size (default: from config)'
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=None,
        help='Trading symbols to train on (default: from config)'
    )
    
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=None,
        help='Learning rate (default: from config)'
    )
    
    parser.add_argument(
        '--validation-split',
        type=float,
        default=0.2,
        help='Validation split ratio (default: 0.2)'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        choices=['cpu', 'cuda'],
        default=None,
        help='Device to train on (default: auto-detect)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='ai_model/logs/training.log',
        help='Log file path'
    )
    
    return parser.parse_args()


def main():
    """Main training function."""
    args = parse_args()
    
    # Setup logger
    logger = setup_logger(log_file=args.log_file)
    logger.info("=" * 80)
    logger.info("CoinScribe AI Model Training")
    logger.info("=" * 80)
    
    # Update config with command line arguments
    training_config = config.training.copy()
    if args.epochs is not None:
        training_config['epochs'] = args.epochs
    if args.batch_size is not None:
        training_config['batch_size'] = args.batch_size
    if args.learning_rate is not None:
        training_config['learning_rate'] = args.learning_rate
    
    logger.info(f"Training configuration: {training_config}")
    
    # Initialize data loader
    logger.info("Initializing data loader...")
    data_loader = MarketDataLoader(config._config)
    
    # Fetch and prepare data
    logger.info("Fetching market data...")
    symbols = args.symbols or config.get('data_sources.market_data.symbols')
    logger.info(f"Using symbols: {symbols}")
    
    df = data_loader.prepare_training_data(symbols=symbols)
    
    if df.empty:
        logger.error("No data available for training. Exiting.")
        return
    
    logger.info(f"Fetched {len(df)} data points")
    
    # Initialize preprocessor
    logger.info("Preprocessing data...")
    preprocessor = DataPreprocessor(config._config)
    
    # Prepare training data
    (X_train, y_train), (X_val, y_val) = preprocessor.prepare_data(
        df,
        validation_split=args.validation_split
    )
    
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")
    logger.info(f"Input shape: {X_train.shape}")
    logger.info(f"Output shape: {y_train.shape}")
    
    # Save scalers
    scaler_path = Path(training_config['checkpoint_dir']) / 'scalers.pkl'
    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    preprocessor.save_scalers(str(scaler_path))
    logger.info(f"Saved scalers to {scaler_path}")
    
    # Initialize model
    logger.info("Initializing model...")
    model = AIIndexModel(
        input_features=X_train.shape[2],  # Number of features
        hidden_size=config.get('model.hidden_size'),
        num_layers=config.get('model.num_layers'),
        output_size=config.get('model.output_size'),
        dropout=config.get('model.dropout')
    )
    
    logger.info(f"Model architecture: {model}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,}")
    
    # Initialize trainer
    logger.info("Initializing trainer...")
    trainer = ModelTrainer(
        model=model,
        config=training_config,
        device=args.device
    )
    
    # Train model
    logger.info("Starting training...")
    history = trainer.train(
        train_data=(X_train, y_train),
        val_data=(X_val, y_val),
        epochs=training_config['epochs'],
        batch_size=training_config['batch_size']
    )
    
    logger.info("Training completed!")
    
    # Plot training history
    logger.info("Generating training plots...")
    plot_path = Path(training_config['checkpoint_dir']) / 'training_history.png'
    plot_training_history(
        train_losses=history['train_losses'],
        val_losses=history['val_losses'],
        save_path=str(plot_path),
        show=False
    )
    
    logger.info(f"Training history plot saved to {plot_path}")
    logger.info("=" * 80)
    logger.info("Training completed successfully!")
    logger.info(f"Best model saved to: {trainer.checkpoint_dir / 'best_model.pth'}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
