# 🕯️ Candles Subnet [Subnet ID: SN31]

A decentralized cryptocurrency candle prediction network built on Bittensor. Miners compete to predict cryptocurrency price movements (candle colors and closing values) for TAO-USD across multiple time intervals, while validators score predictions against real market data.

[Discord](https://discord.gg/MTZP7CJQ) • [Web Interface](https://www.candlestao.com/)

---

## 📚 Table of Contents
- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Model Training](#-model-training)
- [Prediction Files](#-prediction-files)
- [Scoring System](#-scoring-system)
- [Contact](#-contact)

---

## 🧩 About

Candles Subnet is a decentralized prediction market for cryptocurrency price movements on the Bittensor network. The subnet incentivizes miners to develop and deploy accurate prediction models for TAO-USD candle data across hourly, daily, and weekly intervals.

**Vision**: Create a competitive marketplace where miners leverage machine learning, technical analysis, and market insights to generate accurate price predictions, rewarded through Bittensor's incentive mechanism.

**Key Principles**:
- **Decentralized**: Open participation for miners worldwide to compete in prediction accuracy
- **Multi-Interval**: Support for hourly, daily, and weekly prediction horizons
- **Transparent**: Predictions are scored against real market data from CoinDesk
- **Continuous**: 24/7 operation with automatic prediction updates
- **Incentivized**: Economic rewards based on prediction accuracy (both color and price proximity)

---

## ✨ Features

- **Multi-Interval Predictions**: Generate predictions for hourly, daily, and weekly candle intervals
- **Flexible Prediction Sources**: 
  - Use trained LSTM models (via training pipeline)
  - Provide custom CSV prediction files
  - Fallback to random predictions for testing
- **Model Training Pipeline**: Complete training infrastructure in `train/` directory
  - LSTM-based neural network architecture
  - Support for hourly, daily, and weekly model variants
  - Data normalization and preprocessing
  - Historical data fetching from CoinDesk API
- **Automated Prediction Generation**: Continuous prediction updates using trained models
- **File-Based Predictions**: Easy integration with external prediction systems via CSV files
- **Real-time Scoring**: Validators score predictions against actual market data
- **Bittensor Integration**: Native integration with Bittensor network for rewards and consensus

---

## 🧠 Tech Stack

- **Languages**: Python 3.12+
- **Blockchain**: Bittensor (Subnet 31)
- **AI/ML Frameworks**: 
  - PyTorch (for LSTM model training and inference)
  - Pandas (for data processing)
- **Data Sources**: CoinDesk API (TAO-USD historical data)
- **Package Management**: uv (recommended) or pip
- **Process Management**: PM2 (optional, for production)

---

## ⚙️ Installation

### Prerequisites

- Python 3.12 or higher
- Bittensor wallet
- Rust (required for Bittensor)
- Astral uv package manager

### System Requirements

- CPU: 2+ cores (4+ recommended for model training)
- RAM: 8 GB (16 GB recommended for model training)
- Storage: 10 GB free space (SSD recommended)
- GPU: Optional but recommended for model training (CUDA-compatible)
- OS: Ubuntu 20.04+ or similar Linux distribution

### Quick Setup (Automated)

The easiest way to set up your miner is using the automated setup script:

```bash
# Clone the repository
git clone https://github.com/CandlesTAO/candles.git
cd candles

# Run the setup script with your wallet and hotkey names
./setup_miner.sh <wallet_name> <hotkey_name>

# Example:
./setup_miner.sh my_wallet my_hotkey
```

The setup script will:
- Install system dependencies
- Set up Python environment with uv
- Install project dependencies
- Create a custom miner script for your wallet/hotkey
- Run tests to verify installation


### Manual Installation

If you prefer manual setup:

1. **Install Rust** (required for Bittensor):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source ~/.cargo/env
   ```

2. **Install Astral uv** (Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.local/bin/env
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Run tests**:
   ```bash
   uv run pytest tests/ --asyncio-mode=auto
   ```

### Bittensor Wallet Setup

1. Create your Bittensor wallet if you haven't already
2. Register your miner:
   - Testnet: `btcli subnets register --network test --netuid 357`
   - Mainnet: `btcli subnets register --netuid 31`

---

## 🚀 Usage

### Running on Testnet

*Always test your miner on Testnet #357 first*

```bash
# Activate the virtual environment (if using manual setup)
source .venv/bin/activate

# Start the miner (using custom script from setup)
./miner_<wallet_name>_<hotkey_name> \
  --subtensor.network test \
  --netuid 357 \
  --wallet.name YOUR_WALLET_NAME \
  --wallet.hotkey YOUR_HOTKEY_NAME \
  --logging.debug \
  --axon.port LOCAL_PORT \
  --axon.external_port EXTERNAL_PORT \
  --axon.external_ip EXTERNAL_IP
```

Ensure the external endpoint is accessible by validators and check for error logs. You'll start receiving prediction requests shortly.

### Running on Mainnet

```bash
# Register on SN31 (if not already registered)
btcli subnets register --netuid 31

# Start the miner with PM2 (recommended for production)
npm install -g pm2
pm2 start ecosystem.config.js

# Or run directly
./miner_<wallet_name>_<hotkey_name>
```

### Prediction Methods

The miner supports three methods for generating predictions:

1. **File-Based Predictions** (Recommended): Place CSV files in `~/.candles/data/` or use the web interface at [candlestao.com](https://www.candlestao.com/)
2. **Model-Based Predictions**: Use the training pipeline to generate predictions with trained LSTM models
3. **Random Predictions**: Fallback method for testing (not recommended for production)

---

## 🧾 Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# For validators (not required for miners)
COINDESK_API_KEY=your_coindesk_api_key_here
```

### Miner Configuration

Key configuration parameters when running the miner:

- `--netuid`: Subnet ID (357 for testnet, 31 for mainnet)
- `--wallet.name`: Your Bittensor wallet name
- `--wallet.hotkey`: Your Bittensor hotkey name
- `--axon.port`: Local port for the miner endpoint (default: 8092)
- `--axon.external_port`: External port (must be accessible by validators)
- `--axon.external_ip`: Your public IP address
- `--blacklist.validator_min_stake`: Minimum stake required for validators (default: 0)
- `--logging.debug`: Enable debug logging
- `--neuron.epoch_length`: Epoch length in blocks (default: 50)

### Example Configuration

```bash
uv run candles/miner/miner.py \
  --axon.external_ip YOUR_IP_ADDRESS \
  --netuid 31 \
  --axon.port 8091 \
  --wallet.name miner \
  --wallet.hotkey miner_default \
  --blacklist.validator_min_stake 0 \
  --logging.info \
  --neuron.epoch_length 50
```

---

## 🤖 Model Training

The `train/` directory contains a complete training pipeline for LSTM-based candle prediction models.

### Training Overview

The training system supports three model variants:
- **Hourly Model**: Predicts next hour candle (10-minute intervals)
- **Daily Model**: Predicts next day candle (4-hour intervals)
- **Weekly Model**: Predicts next week candle (1-day intervals)

### Training Steps

1. **Download Historical Data**:
   ```bash
   cd train
   # Update config.py to set dataset_type: 'hourly', 'daily', or 'weekly'
   python download.py
   ```

2. **Normalize Data**:
   ```bash
   python normalization.py
   ```

3. **Train Model**:
   ```bash
   python train.py
   ```

4. **Generate Predictions**:
   ```bash
   python prediction.py
   ```

The `prediction.py` script runs continuously and:
- Fetches latest TAO-USD data from CoinDesk API
- Generates predictions using trained models
- Saves predictions to `~/.candles/data/` in CSV format
- Updates predictions automatically (hourly every 30 min, daily every 12 hours, weekly every 3 days)

### Model Architecture

- **Architecture**: LSTM (Long Short-Term Memory) neural network
- **Input Features**: close, high, low, volume, volume_top_tier, volume_direct
- **Input Length**: 
  - Hourly: 144 timesteps (24 hours of 10-minute intervals)
  - Daily: 120 timesteps (20 days of 4-hour intervals)
  - Weekly: 70 timesteps (10 weeks of 1-day intervals)
- **Output**: Predicted closing prices for future intervals
- **Training**: Adam optimizer with learning rate scheduling

---

## 🔮 Prediction Files

Miners can provide their own predictions instead of using random generation by placing CSV files in specific locations. The miner will automatically detect and use these files when available.

### Web Interface for Predictions Generation

Create and download prediction CSV files easily using the web interface at:
**[candlestao.com](https://www.candlestao.com/)**

This web tool allows you to generate properly formatted prediction files without manually creating CSV files.

### File Placement Options

```bash
# Create the candles data directory
mkdir -p ~/.candles/data/

# Place your prediction files here with these exact names:
~/.candles/data/hourly_predictions.csv   # For hourly predictions
~/.candles/data/daily_predictions.csv    # For daily predictions
~/.candles/data/weekly_predictions.csv   # For weekly predictions
```

### CSV File Format

Your prediction files must follow this exact format:

```csv
timestamp,color,confidence,price
1704067200,red,0.85,45.50
1704070800,green,0.92,46.20
1704074400,red,0.78,44.90
```

**Column Requirements:**
- `timestamp`: Unix timestamp for the prediction interval start time
- `color`: Predicted candle color (`red` or `green`)
- `confidence`: Confidence level (0.0 to 1.0)
- `price`: Predicted closing price (decimal number)

### How It Works

1. **File Discovery**: The miner searches for prediction files in this order:
   - `~/.candles/data/[interval]_predictions.csv` (e.g., `hourly_predictions.csv`)
   - If no files found, generates random predictions

2. **Prediction Matching**: When a validator requests a prediction:
   - Miner loads predictions from the appropriate file
   - Filters predictions to only include future intervals
   - Matches the exact `interval_id` requested by the validator
   - Returns the matching prediction if found

3. **Fallback Behavior**: If no prediction file is found or no matching prediction exists, the miner automatically generates random predictions to ensure continuous operation.

---

## 📊 Scoring System

The scoring framework evaluates miners based on prediction accuracy:

- **Color Accuracy**: Correctly predicting whether the candle will be red (price decrease) or green (price increase)
- **Price Proximity**: How close the predicted closing price is to the actual closing price
- **Confidence Calibration**: Confidence scores should reflect actual prediction accuracy

**Performance Expectations**:
- Higher accuracy predictions receive more rewards
- Consistent performance over time is rewarded
- Predictions are scored against real market data from CoinDesk

---

## 🖼 Screenshots

<div align="center">

![Candles Subnet](candles_sn31.png)

</div>

---

## 📜 API Documentation

The project uses Bittensor's synapse protocol. Key synapse types:

- **GetCandlePrediction**: Main synapse sent by validators to miners requesting predictions
  - Contains: `interval` (hourly/daily/weekly), `interval_id` (specific timestamp)
  - Response: `CandlePrediction` with color, price, confidence, and metadata

For detailed protocol definitions, see `candles/core/synapse.py` and `candles/core/data.py`.

---

## 📬 Contact

- **Author**: OKS
- **Email**: james.martin.aitechguy@gmail.com
- **GitHub**: [@lexapp21003](https://github.com/lexapp21003)

---

## 🌟 Acknowledgements

- Built on the [Bittensor](https://github.com/opentensor/bittensor) network
- Market data provided by [CoinDesk](https://www.coindesk.com/)
- Community contributions and feedback from miners and validators