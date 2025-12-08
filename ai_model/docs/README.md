# CoinScribe AI Model Documentation

## Overview

The CoinScribe AI Model is an advanced machine learning system designed to generate investment indices based on historical cryptocurrency market data and news sentiment. This documentation provides comprehensive guidance on using, training, and integrating the AI model into the CoinScribe platform.

## Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Training the Model](#training-the-model)
5. [API Usage](#api-usage)
6. [Configuration](#configuration)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)

## Architecture

### System Components

The AI model system consists of several key components:

1. **Model Architecture** (`ai_model/models/training/model_architecture.py`)
   - LSTM-based neural network for time series prediction
   - Multi-head attention mechanism for focusing on important patterns
   - Fully connected layers for index generation

2. **Data Pipeline** (`ai_model/data/pipelines/`)
   - `data_loader.py`: Fetches market data from various sources (yfinance)
   - `preprocessor.py`: Preprocesses and normalizes data for training

3. **Training System** (`ai_model/models/training/trainer.py`)
   - Handles model training with early stopping
   - Implements learning rate scheduling
   - Saves checkpoints and training history

4. **Inference System** (`ai_model/models/inference/predictor.py`)
   - Loads trained models for prediction
   - Provides convenient prediction interfaces
   - Handles data preprocessing for inference

5. **API Server** (`ai_model/api/endpoints.py`)
   - Flask-based REST API
   - Endpoints for predictions, data fetching, and configuration
   - CORS support for web integration

### Model Details

**Architecture Type**: LSTM with Attention

**Key Features**:
- Time series processing with LSTM layers
- Multi-head attention for pattern recognition
- Batch normalization for training stability
- Dropout for regularization

**Input**: Sequences of market data (default: 60 time steps)
- Price data (open, high, low, close)
- Volume data
- Technical indicators (MA, EMA, MACD, RSI, etc.)
- Sentiment scores (from news analysis)

**Output**: 10 investment indices representing different market aspects

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster training

### Steps

1. Clone the repository:
```bash
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -c "import torch; import pandas; print('Installation successful!')"
```

## Quick Start

### 1. Fetch Market Data

```python
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.config import config

# Initialize data loader
data_loader = MarketDataLoader(config._config)

# Fetch data for Bitcoin
df = data_loader.fetch_market_data('BTC-USD', period='1mo', interval='1h')
print(df.head())
```

### 2. Train the Model

```bash
# Basic training with default configuration
python train_model.py

# Training with custom parameters
python train_model.py --epochs 50 --batch-size 64 --symbols BTC-USD ETH-USD
```

### 3. Run the API Server

```bash
# Start the server
python run_server.py

# With custom host and port
python run_server.py --host 0.0.0.0 --port 5000 --debug
```

### 4. Make Predictions

```python
from ai_model.models.inference.predictor import AIIndexPredictor
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.config import config

# Initialize predictor
predictor = AIIndexPredictor(
    model_path='ai_model/models/checkpoints/best_model.pth',
    config=config._config
)

# Initialize data loader
data_loader = MarketDataLoader(config._config)

# Make predictions
result = predictor.predict_next_indices(
    symbols=['BTC-USD', 'ETH-USD'],
    data_loader=data_loader
)

print(f"Predicted Indices: {result['indices']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Training the Model

### Basic Training

The training process involves:
1. Fetching historical market data
2. Preprocessing and creating sequences
3. Training with validation
4. Saving checkpoints

```bash
python train_model.py
```

### Advanced Training Options

```bash
python train_model.py \
    --epochs 100 \
    --batch-size 32 \
    --learning-rate 0.001 \
    --symbols BTC-USD ETH-USD BNB-USD ADA-USD SOL-USD \
    --validation-split 0.2 \
    --device cuda
```

### Training Parameters

- `--epochs`: Number of training epochs (default: from config)
- `--batch-size`: Batch size for training (default: 32)
- `--learning-rate`: Learning rate (default: 0.001)
- `--symbols`: List of crypto symbols to train on
- `--validation-split`: Validation data ratio (default: 0.2)
- `--device`: Training device ('cpu' or 'cuda')

### Monitoring Training

Training logs are saved to `ai_model/logs/training.log`

Training history plot is saved to `ai_model/models/checkpoints/training_history.png`

Checkpoints are saved to `ai_model/models/checkpoints/`

## API Usage

### Starting the Server

```bash
python run_server.py --host 0.0.0.0 --port 5000
```

### API Endpoints

#### 1. Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "0.1.0"
}
```

#### 2. Get Model Information
```
GET /api/model/info
```

Response:
```json
{
  "model_path": "ai_model/models/checkpoints/best_model.pth",
  "device": "cuda",
  "architecture": "lstm",
  "input_features": 32,
  "hidden_size": 128,
  "num_layers": 2,
  "output_size": 10
}
```

#### 3. Predict Indices
```
POST /api/predict/indices
Content-Type: application/json

{
  "symbols": ["BTC-USD", "ETH-USD"],
  "period": "1mo",
  "interval": "1h"
}
```

Response:
```json
{
  "indices": [0.75, 0.82, 0.68, 0.91, 0.77, 0.85, 0.73, 0.88, 0.79, 0.84],
  "index_names": ["Index_1", "Index_2", ..., "Index_10"],
  "confidence": 0.85,
  "symbols": ["BTC-USD", "ETH-USD"],
  "timestamp": "2024-01-01 12:00:00"
}
```

#### 4. Fetch Market Data
```
POST /api/data/fetch
Content-Type: application/json

{
  "symbols": ["BTC-USD"],
  "period": "1mo",
  "interval": "1d"
}
```

Response:
```json
{
  "data": [...],
  "count": 30,
  "symbols": ["BTC-USD"],
  "columns": ["Open", "High", "Low", "Close", "Volume", ...]
}
```

#### 5. List Available Indices
```
GET /api/indices/list
```

Response:
```json
{
  "indices": [
    {
      "name": "Index_1",
      "description": "AI-generated investment index 1",
      "type": "composite"
    },
    ...
  ],
  "count": 10
}
```

### Using the API with curl

```bash
# Health check
curl http://localhost:5000/health

# Get model info
curl http://localhost:5000/api/model/info

# Predict indices
curl -X POST http://localhost:5000/api/predict/indices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC-USD", "ETH-USD"]}'

# Fetch market data
curl -X POST http://localhost:5000/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC-USD"], "period": "1mo", "interval": "1d"}'
```

### Using the API with Python

```python
import requests

# Predict indices
response = requests.post(
    'http://localhost:5000/api/predict/indices',
    json={'symbols': ['BTC-USD', 'ETH-USD']}
)

result = response.json()
print(f"Indices: {result['indices']}")
print(f"Confidence: {result['confidence']}")
```

## Configuration

Configuration is managed through `ai_model/config/config.yaml`

### Key Configuration Sections

#### Model Configuration
```yaml
model:
  architecture: "lstm"
  input_features: 32
  hidden_size: 128
  num_layers: 2
  output_size: 10
  dropout: 0.2
```

#### Training Configuration
```yaml
training:
  batch_size: 32
  learning_rate: 0.001
  epochs: 100
  validation_split: 0.2
  early_stopping_patience: 10
  checkpoint_dir: "ai_model/models/checkpoints"
```

#### Data Configuration
```yaml
data:
  sequence_length: 60
  features:
    - "open"
    - "high"
    - "low"
    - "close"
    - "volume"
    - "market_cap"
    - "sentiment_score"
  normalize: true
```

#### API Configuration
```yaml
api:
  host: "0.0.0.0"
  port: 5000
  debug: false
  cors_origins: ["*"]
```

## Development

### Project Structure

```
ai_model/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── config.yaml
├── models/
│   ├── __init__.py
│   ├── training/
│   │   ├── __init__.py
│   │   ├── model_architecture.py
│   │   └── trainer.py
│   └── inference/
│       ├── __init__.py
│       └── predictor.py
├── data/
│   ├── __init__.py
│   └── pipelines/
│       ├── __init__.py
│       ├── data_loader.py
│       └── preprocessor.py
├── api/
│   ├── __init__.py
│   └── endpoints.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── visualization.py
└── docs/
    └── README.md
```

### Adding New Features

1. **Adding New Data Sources**:
   - Extend `MarketDataLoader` in `data/pipelines/data_loader.py`
   - Update configuration in `config/config.yaml`

2. **Adding New Technical Indicators**:
   - Add methods to `MarketDataLoader.add_technical_indicators()`
   - Update feature list in configuration

3. **Modifying Model Architecture**:
   - Edit `AIIndexModel` in `models/training/model_architecture.py`
   - Update model configuration

4. **Adding API Endpoints**:
   - Add routes to `api/endpoints.py`
   - Update documentation

### Testing

Run example usage:
```bash
python example_usage.py
```

Test API endpoints:
```bash
# Start server in one terminal
python run_server.py

# Test in another terminal
curl http://localhost:5000/health
```

## Troubleshooting

### Common Issues

1. **Model Not Found Error**
   - Train the model first: `python train_model.py`
   - Check model path in configuration

2. **No Data Retrieved**
   - Check internet connection
   - Verify symbol names (use Yahoo Finance format, e.g., 'BTC-USD')
   - Try different time periods

3. **CUDA Out of Memory**
   - Reduce batch size: `--batch-size 16`
   - Use CPU: `--device cpu`
   - Reduce sequence length in config

4. **API Connection Issues**
   - Check if server is running: `curl http://localhost:5000/health`
   - Verify host and port settings
   - Check firewall rules

### Getting Help

For issues and questions:
1. Check the documentation
2. Review example usage scripts
3. Check logs in `ai_model/logs/`
4. Open an issue on GitHub

## Future Enhancements

Planned features:
1. Integration with real-time news sentiment API
2. Support for more data sources (Binance, CoinGecko, etc.)
3. Advanced model architectures (Transformers, GRU)
4. Automated model retraining
5. Performance metrics dashboard
6. Multi-timeframe analysis
7. Portfolio optimization features

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See LICENSE file in the repository root.
