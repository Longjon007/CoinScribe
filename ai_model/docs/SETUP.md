# Setup and Installation Guide

## Prerequisites

Before setting up the CoinScribe AI Model, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM (8GB+ recommended for training)
- (Optional) CUDA-capable GPU with 4GB+ VRAM for faster training

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyTorch (>=2.6.0) - Deep learning framework
- NumPy (>=1.24.0) - Numerical computing
- Pandas (>=2.0.0) - Data manipulation
- scikit-learn (>=1.3.0) - Machine learning utilities
- yfinance (>=0.2.28) - Market data fetching
- Flask (>=3.0.0) - API server
- And other dependencies

### 4. Verify Installation

```bash
python3 -c "import torch; import pandas; import flask; print('✓ All dependencies installed successfully')"
```

### 5. Initial Setup

Create necessary directories:
```bash
mkdir -p ai_model/logs
mkdir -p ai_model/models/checkpoints
```

## Quick Start

### Option 1: Train Your Own Model

1. Train the model with default settings:
```bash
python train_model.py
```

2. Wait for training to complete (this may take 30-60 minutes depending on your hardware)

3. Check the results:
   - Model checkpoint: `ai_model/models/checkpoints/best_model.pth`
   - Training history: `ai_model/models/checkpoints/training_history.json`
   - Training plot: `ai_model/models/checkpoints/training_history.png`

### Option 2: Start the API Server

Even without a trained model, you can start the API server:

```bash
python run_server.py
```

The server will start on `http://localhost:5000`. You can access:
- Health check: `http://localhost:5000/health`
- API documentation: See `ai_model/docs/API.md`

### Option 3: Run Examples

```bash
python example_usage.py
```

This interactive script lets you:
1. Fetch market data
2. View model information
3. Make predictions (requires trained model)

## Training Configuration

### Default Training

```bash
python train_model.py
```

Uses settings from `ai_model/config/config.yaml`:
- Epochs: 100
- Batch size: 32
- Learning rate: 0.001
- Symbols: BTC-USD, ETH-USD, BNB-USD, ADA-USD, SOL-USD

### Custom Training

```bash
# Train for 50 epochs with batch size 64
python train_model.py --epochs 50 --batch-size 64

# Train on specific symbols
python train_model.py --symbols BTC-USD ETH-USD

# Use GPU if available
python train_model.py --device cuda

# Combine multiple options
python train_model.py \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.001 \
  --symbols BTC-USD ETH-USD BNB-USD \
  --device cuda
```

## API Server Configuration

### Default Server

```bash
python run_server.py
```

Server starts on `http://0.0.0.0:5000`

### Custom Configuration

```bash
# Custom host and port
python run_server.py --host localhost --port 8080

# Debug mode (auto-reload on code changes)
python run_server.py --debug
```

### Configuration File

Edit `ai_model/config/config.yaml` to change:
- Model parameters
- Training settings
- Data sources
- API configuration

## Troubleshooting

### Issue: ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'torch'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: CUDA Out of Memory

**Problem**: Training fails with CUDA out of memory error

**Solutions**:
1. Reduce batch size:
   ```bash
   python train_model.py --batch-size 16
   ```

2. Use CPU instead:
   ```bash
   python train_model.py --device cpu
   ```

3. Reduce sequence length in config.yaml:
   ```yaml
   data:
     sequence_length: 30  # Reduced from 60
   ```

### Issue: No Data Retrieved

**Problem**: "No data available for training"

**Solutions**:
1. Check internet connection
2. Verify symbol format (use Yahoo Finance format like 'BTC-USD')
3. Try different time periods:
   ```bash
   # In config.yaml, change:
   data_sources:
     market_data:
       period: "6mo"  # Instead of "1y"
   ```

### Issue: API Server Won't Start

**Problem**: Port already in use

**Solution**: Use a different port:
```bash
python run_server.py --port 8080
```

### Issue: Slow Training

**Problem**: Training is very slow on CPU

**Solutions**:
1. Install CUDA-enabled PyTorch if you have a GPU:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. Reduce dataset size by limiting symbols or period

3. Use a smaller model:
   ```yaml
   # In config.yaml:
   model:
     hidden_size: 64  # Reduced from 128
     num_layers: 1    # Reduced from 2
   ```

## Updating

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstalling

To remove the installation:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove model checkpoints (optional)
rm -rf ai_model/models/checkpoints/*

# Remove logs (optional)
rm -rf ai_model/logs/*
```

## Next Steps

After successful installation:

1. Read the [Main Documentation](README.md)
2. Review the [API Documentation](API.md)
3. Try the example scripts
4. Train your first model
5. Start building your application!

## Support

If you encounter issues:
1. Check this guide
2. Review logs in `ai_model/logs/`
3. Check GitHub Issues
4. Open a new issue with:
   - Error message
   - Your setup (OS, Python version, GPU/CPU)
   - Steps to reproduce

## System Requirements

### Minimum Requirements
- CPU: 2 cores
- RAM: 4GB
- Storage: 2GB free space
- OS: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Recommended Requirements
- CPU: 4+ cores
- RAM: 8GB+
- GPU: CUDA-capable with 4GB+ VRAM
- Storage: 10GB+ free space
- OS: Linux (Ubuntu 20.04+) or Windows 11

### Training Performance Estimates

| Hardware | Training Time (100 epochs) |
|----------|---------------------------|
| CPU only | 2-4 hours |
| GPU (entry-level) | 30-60 minutes |
| GPU (high-end) | 15-30 minutes |

*Times are approximate and depend on dataset size and configuration*
