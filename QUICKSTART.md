# CoinScribe AI Model - Quick Start Guide

Get up and running with the CoinScribe AI model in 5 minutes!

## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Three Ways to Use

### 1. Train Your Own Model (30-60 minutes)

```bash
python train_model.py
```

This will:
- ✅ Fetch historical market data for BTC, ETH, BNB, ADA, SOL
- ✅ Train an LSTM model with attention mechanism
- ✅ Save the best model to `ai_model/models/checkpoints/best_model.pth`
- ✅ Generate training history plot

**Custom training:**
```bash
python train_model.py --epochs 50 --batch-size 64 --symbols BTC-USD ETH-USD
```

### 2. Start the API Server

```bash
python run_server.py
```

Server starts at `http://localhost:5000`

**Test it:**
```bash
# Health check
curl http://localhost:5000/health

# Predict indices
curl -X POST http://localhost:5000/api/predict/indices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC-USD", "ETH-USD"]}'
```

### 3. Use in Your Python Code

```python
from ai_model.models.inference.predictor import AIIndexPredictor
from ai_model.data.pipelines.data_loader import MarketDataLoader
from ai_model.config import config

# Initialize
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

## 📊 Example Usage

Run the interactive example:

```bash
python example_usage.py
```

Choose from:
1. Fetch Market Data
2. Display Model Information
3. Predict Investment Indices
4. Run All Examples

## 🔧 Configuration

Edit `ai_model/config/config.yaml` to customize:

```yaml
# Model settings
model:
  hidden_size: 128
  num_layers: 2
  output_size: 10

# Training settings
training:
  batch_size: 32
  learning_rate: 0.001
  epochs: 100

# Data settings
data:
  sequence_length: 60
  features:
    - "open"
    - "high"
    - "low"
    - "close"
    - "volume"
```

## 🐛 Common Issues

### No Module Named 'torch'
```bash
pip install -r requirements.txt
```

### CUDA Out of Memory
```bash
python train_model.py --device cpu --batch-size 16
```

### No Data Retrieved
- Check internet connection
- Verify symbol format (use 'BTC-USD', not 'BTC')

## 📚 Next Steps

1. **Read Full Documentation**: `ai_model/docs/README.md`
2. **API Reference**: `ai_model/docs/API.md`
3. **Setup Guide**: `ai_model/docs/SETUP.md`
4. **Installation Options**: `INSTALL.md`

## 🎓 Learn More

### Project Structure
```
CoinScribe/
├── train_model.py          # Train the AI model
├── run_server.py           # Start API server
├── example_usage.py        # Interactive examples
├── requirements.txt        # Dependencies
└── ai_model/               # Main package
    ├── models/            # Model architecture
    ├── data/              # Data pipeline
    ├── api/               # REST API
    └── docs/              # Documentation
```

### Key Commands

```bash
# Training
python train_model.py --help

# API Server
python run_server.py --help

# Check installation
python -c "from ai_model.config import config; print('✓ Ready!')"
```

## 💡 Pro Tips

1. **Use GPU**: Add `--device cuda` for 10x faster training
2. **Custom Symbols**: Add `--symbols YOUR-SYMBOLS` to train on specific coins
3. **Debug Mode**: Run server with `--debug` for auto-reload during development
4. **Check Logs**: View `ai_model/logs/` for detailed information

## 🤝 Need Help?

- Check documentation in `ai_model/docs/`
- Review examples in `example_usage.py`
- Check GitHub Issues
- Read `ai_model/docs/SETUP.md` for troubleshooting

## ✨ Features

- 🧠 **LSTM with Attention** - Advanced neural network
- 📈 **Technical Indicators** - MA, EMA, MACD, RSI, and more
- 🔌 **REST API** - Easy integration
- ⚙️ **Configurable** - Customize everything
- 📊 **Visualizations** - Training history plots
- 🔒 **Secure** - No vulnerabilities (CodeQL verified)

---

**Ready to start?** Run `python train_model.py` now!
