# CoinScribe

CoinScribe is an all-in-one crypto tracker that shows you not just what the market is doing, but why. It goes beyond simple price charts by integrating a powerful AI engine that instantly reads, understands, and summarizes the latest news for any coin.

## 🚀 New Feature: AI Investment Index Creation

CoinScribe now includes an advanced AI model that generates investment indices based on historical market data and news sentiment. This feature helps investors make data-driven decisions by analyzing market trends and predicting future movements.

### Key Features

- **LSTM-based Neural Network**: Advanced time series prediction using LSTM architecture with attention mechanism
- **Multi-Source Data Integration**: Combines price data, technical indicators, and sentiment analysis
- **Real-time Predictions**: REST API for generating investment indices on demand
- **Flexible Configuration**: Easily customizable model parameters and data sources
- **Comprehensive Documentation**: Full API documentation and usage examples

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster training

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the AI model:
```bash
python train_model.py
```

4. Start the API server:
```bash
python run_server.py
```

## 🎯 Quick Start

### Train the Model

```bash
# Basic training with default configuration
python train_model.py

# Advanced training with custom parameters
python train_model.py --epochs 50 --batch-size 64 --symbols BTC-USD ETH-USD
```

### Run the API Server

```bash
# Start server on default port (5000)
python run_server.py

# Custom configuration
python run_server.py --host 0.0.0.0 --port 8080 --debug
```

### Make Predictions

```python
from ai_model.models.inference.predictor import AIIndexPredictor
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.config import config

# Initialize components
predictor = AIIndexPredictor(
    model_path='ai_model/models/checkpoints/best_model.pth',
    config=config._config
)
data_loader = MarketDataLoader(config._config)

# Make predictions
result = predictor.predict_next_indices(
    symbols=['BTC-USD', 'ETH-USD'],
    data_loader=data_loader
)

print(f"Predicted Indices: {result['indices']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Use the REST API

```bash
# Check health
curl http://localhost:5000/health

# Get model information
curl http://localhost:5000/api/model/info

# Predict indices
curl -X POST http://localhost:5000/api/predict/indices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC-USD", "ETH-USD"]}'
```

## 📚 Documentation

Comprehensive documentation is available in the `ai_model/docs/` directory:

- **[Main Documentation](ai_model/docs/README.md)**: Complete guide to installation, training, and usage
- **[API Documentation](ai_model/docs/API.md)**: Detailed REST API reference

### API Endpoints

- `GET /health` - Health check
- `GET /api/model/info` - Get model information
- `POST /api/predict/indices` - Predict investment indices
- `POST /api/data/fetch` - Fetch market data
- `GET /api/indices/list` - List available indices
- `GET /api/config` - Get API configuration

## 🏗️ Architecture

### Components

1. **Model Architecture** (`ai_model/models/training/`)
   - LSTM-based neural network
   - Multi-head attention mechanism
   - Fully connected prediction layers

2. **Data Pipeline** (`ai_model/data/pipelines/`)
   - Market data fetching (yfinance)
   - Technical indicators calculation
   - Data preprocessing and normalization

3. **Training System** (`ai_model/models/training/`)
   - Model training with early stopping
   - Learning rate scheduling
   - Checkpoint management

4. **Inference System** (`ai_model/models/inference/`)
   - Model loading and prediction
   - Batch and real-time inference

5. **API Server** (`ai_model/api/`)
   - Flask-based REST API
   - CORS support
   - Error handling

## 📊 Model Details

- **Architecture**: LSTM with Multi-Head Attention
- **Input**: 60-step sequences of market data
- **Features**: Price (OHLC), Volume, Technical Indicators (MA, EMA, MACD, RSI), Sentiment Scores
- **Output**: 10 investment indices
- **Training**: PyTorch with Adam optimizer and learning rate scheduling

## 🛠️ Configuration

Configuration is managed through `ai_model/config/config.yaml`. Key settings include:

- Model architecture parameters
- Training hyperparameters
- Data sources and features
- API server settings

## 📝 Examples

Run the example script to see the AI model in action:

```bash
python example_usage.py
```

This interactive script demonstrates:
- Fetching market data
- Displaying model information
- Making predictions

## 💻 Development

### Code Structure

The codebase is organized as follows:

- `ai_model/`: Main package directory
  - `api/`: API server and endpoints
  - `config/`: Configuration management
  - `data/`: Data loading and preprocessing pipelines
  - `models/`: Neural network architecture and training logic
  - `utils/`: Helper utilities (logging, visualization)
- `tests/`: Test suite
- `example_usage.py`: Interactive example script
- `run_server.py`: API server entry point
- `train_model.py`: Training script entry point

### Documentation

The codebase is fully documented with docstrings following Google Python Style Guide.
Detailed documentation is available in the `ai_model/docs/` directory.

### Running Tests

To run the test suite:

```bash
pytest
```

To run with coverage report:

```bash
pytest --cov=ai_model tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

See LICENSE file for details.

## 🔮 Future Enhancements

- Real-time news sentiment integration
- Support for additional data sources (Binance, CoinGecko)
- Advanced model architectures (Transformers)
- Automated model retraining
- Portfolio optimization features
- WebSocket support for real-time updates
