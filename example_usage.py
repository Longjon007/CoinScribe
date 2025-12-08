#!/usr/bin/env python3
"""
Example Usage of CoinScribe AI Model
=====================================

This script demonstrates how to use the AI model for making predictions.
"""

import sys
from pathlib import Path

# Add ai_model to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_model.config import config
from ai_model.models.inference.predictor import AIIndexPredictor
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.utils.logger import setup_logger


def example_predict_indices():
    """Example: Predict AI indices for crypto symbols."""
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("Example: Predicting AI Investment Indices")
    logger.info("=" * 80)
    
    # Initialize components
    logger.info("Initializing predictor and data loader...")
    
    model_path = config.get('serving.model_path', 'ai_model/models/checkpoints/best_model.pth')
    predictor = AIIndexPredictor(
        model_path=model_path,
        config=config._config
    )
    
    data_loader = MarketDataLoader(config._config)
    
    # Define symbols to analyze
    symbols = ['BTC-USD', 'ETH-USD', 'BNB-USD']
    logger.info(f"Analyzing symbols: {symbols}")
    
    # Make predictions
    logger.info("Fetching data and making predictions...")
    
    try:
        result = predictor.predict_next_indices(
            symbols=symbols,
            data_loader=data_loader
        )
        
        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("PREDICTION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Symbols analyzed: {', '.join(result['symbols'])}")
        logger.info(f"Confidence score: {result['confidence']:.2%}")
        logger.info("\nPredicted Indices:")
        
        for name, value in zip(result['index_names'], result['indices']):
            logger.info(f"  {name}: {value:.4f}")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        logger.info("\nNote: If the model hasn't been trained yet, run 'python train_model.py' first.")


def example_fetch_data():
    """Example: Fetch and display market data."""
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("Example: Fetching Market Data")
    logger.info("=" * 80)
    
    # Initialize data loader
    data_loader = MarketDataLoader(config._config)
    
    # Fetch data for Bitcoin
    symbol = 'BTC-USD'
    logger.info(f"Fetching data for {symbol}...")
    
    df = data_loader.fetch_market_data(
        symbol=symbol,
        period='1mo',
        interval='1d'
    )
    
    if not df.empty:
        logger.info(f"\nFetched {len(df)} records")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info("\nFirst 5 records:")
        logger.info(df.head().to_string())
        
        # Add technical indicators
        logger.info("\nAdding technical indicators...")
        df_with_indicators = data_loader.add_technical_indicators(df)
        logger.info(f"Added indicators: {[col for col in df_with_indicators.columns if col not in df.columns]}")
    else:
        logger.error("No data retrieved")
    
    logger.info("=" * 80)


def example_model_info():
    """Example: Display model information."""
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("Example: Model Information")
    logger.info("=" * 80)
    
    model_path = config.get('serving.model_path', 'ai_model/models/checkpoints/best_model.pth')
    predictor = AIIndexPredictor(
        model_path=model_path,
        config=config._config
    )
    
    info = predictor.get_model_info()
    
    logger.info("\nModel Configuration:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("=" * 80)


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("CoinScribe AI Model - Usage Examples")
    print("="*80 + "\n")
    
    print("Available examples:")
    print("1. Fetch Market Data")
    print("2. Display Model Information")
    print("3. Predict Investment Indices")
    print("4. Run All Examples")
    
    choice = input("\nSelect an example (1-4): ").strip()
    
    print()
    
    if choice == '1':
        example_fetch_data()
    elif choice == '2':
        example_model_info()
    elif choice == '3':
        example_predict_indices()
    elif choice == '4':
        example_fetch_data()
        print("\n")
        example_model_info()
        print("\n")
        example_predict_indices()
    else:
        print("Invalid choice. Please run again and select 1-4.")


if __name__ == '__main__':
    main()
