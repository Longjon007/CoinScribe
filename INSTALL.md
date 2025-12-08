# Installation Guide

## Method 1: Direct Installation (Recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Scripts Directly

```bash
# Train the model
python train_model.py

# Start the API server
python run_server.py

# Run examples
python example_usage.py
```

## Method 2: Package Installation

### Install as a Python Package

```bash
# Clone the repository
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe

# Install in development mode
pip install -e .
```

This makes the package importable from anywhere:

```python
from ai_model.models.inference.predictor import AIIndexPredictor
from ai_model.data.pipelines.data_loader import MarketDataLoader
```

And provides command-line tools:

```bash
# Train the model
coinscribe-train

# Start the API server
coinscribe-serve

# Run examples
coinscribe-example
```

## Method 3: Virtual Environment (Isolated)

### Using venv

```bash
# Create virtual environment
python3 -m venv coinscribe-env

# Activate it
source coinscribe-env/bin/activate  # On Linux/macOS
# or
coinscribe-env\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run scripts
python train_model.py
```

### Using conda

```bash
# Create conda environment
conda create -n coinscribe python=3.10

# Activate it
conda activate coinscribe

# Install dependencies
pip install -r requirements.txt

# Run scripts
python train_model.py
```

## Verification

After installation, verify everything works:

```bash
# Check Python version
python --version  # Should be 3.8 or higher

# Verify syntax of all files
python -m py_compile train_model.py run_server.py example_usage.py

# Check imports (requires dependencies installed)
python -c "from ai_model.config import config; print('✓ Installation successful')"
```

## GPU Support (Optional)

For faster training with NVIDIA GPU:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU is available
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## Troubleshooting

### Issue: Permission Denied

```bash
# Use --user flag
pip install --user -r requirements.txt
```

### Issue: Old pip Version

```bash
# Upgrade pip
pip install --upgrade pip
```

### Issue: Dependency Conflicts

```bash
# Use fresh virtual environment
python3 -m venv fresh-env
source fresh-env/bin/activate
pip install -r requirements.txt
```

## Next Steps

After installation:
1. Read [SETUP.md](ai_model/docs/SETUP.md) for configuration
2. Review [README.md](ai_model/docs/README.md) for usage
3. Check [API.md](ai_model/docs/API.md) for API reference
