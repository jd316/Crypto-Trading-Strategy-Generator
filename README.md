# Crypto Trading Strategy Generator

A powerful application that uses Azure OpenAI to interpret natural language trading strategies, generate executable Python code, and backtest them against real-time cryptocurrency market data from Binance.

![Crypto Trading Strategy Generator](https://raw.githubusercontent.com/user/repo/main/docs/screenshot.png)

## Features

- **Natural Language Processing**: Describe your trading strategy in plain English
- **Automated Code Generation**: Convert natural language into optimized Python trading code
- **Real-Time Market Data**: Connect to Binance for real cryptocurrency OHLCV data
- **Professional Backtesting**: Test strategies with detailed performance metrics
- **Interactive Visualization**: View equity curves and trade logs
- **Azure OpenAI Integration**: Leverage the power of Azure OpenAI for strategy interpretation and code generation

## Requirements

- Python 3.7+ (3.13+ recommended)
- Azure OpenAI API key and endpoint
- Binance API key and secret (for live data)

## Installation

### Option 1: Local Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd crypto-trading-strategy-generator
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the root directory with the following:

   ```
   AZURE_API_KEY=your_azure_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-azure-instance.openai.azure.com
   AZURE_DEPLOYMENT_NAME=your_deployment_name
   AZURE_API_VERSION=2025-01-01-preview
   
   BINANCE_TESTNET_API_KEY=your_binance_api_key_here
   BINANCE_TESTNET_API_SECRET=your_binance_api_secret_here
   ```

### Option 2: Docker Installation

1. Build the Docker image:

   ```bash
   docker build -t crypto-strategy-generator .
   ```

2. Run the container:

   ```bash
   docker run -p 8501:8501 \
     -e AZURE_API_KEY=your_azure_api_key_here \
     -e AZURE_OPENAI_ENDPOINT=your_endpoint \
     -e AZURE_DEPLOYMENT_NAME=your_deployment_name \
     -e BINANCE_TESTNET_API_KEY=your_binance_key \
     -e BINANCE_TESTNET_API_SECRET=your_binance_secret \
     crypto-strategy-generator
   ```

## Quick Start

1. Clone or download the repository
2. Navigate to the project directory

### On Windows

```bash
# Simply run the batch file
run_app.bat
```

### On macOS/Linux

```bash
# First make the script executable (one-time only)
chmod +x run_app.sh

# Then run it
./run_app.sh
```

The script will automatically:

- Create a virtual environment if needed
- Install all required dependencies
- Test imports to verify everything works
- Start the Streamlit application

### macOS-specific Notes

If you encounter issues with TA-Lib installation, install it via Homebrew:

```bash
brew install ta-lib
```

### Linux-specific Notes

If you encounter cryptography build errors, install these packages:

```bash
sudo apt-get update
sudo apt-get install build-essential libssl-dev
```

## Usage

1. Start the Streamlit application using the provided scripts:

   ```bash
   # On Windows
   run_app.bat
   
   # On macOS/Linux
   chmod +x run_app.sh  # Make the script executable (first time only)
   ./run_app.sh
   ```

   Alternatively, you can start it manually:

   ```bash
   # Activate virtual environment first
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   
   # Then run the app
   streamlit run main.py
   Or, venv\Scripts\streamlit run main.py
   ```

2. Access the app in your browser at `http://localhost:8501`

3. Enter your trading strategy in natural language, for example:

   ```
   Buy 0.5 BTC when the 50-period EMA crosses above the 200-period EMA and RSI(14) is below 40,
   exit when RSI(14) exceeds 70 or MACD shows a bearish crossover with a 1h time period
   ```

4. Follow the steps in the UI to:
   - Generate strategy parameters
   - Visualize historical data
   - Generate Python code
   - Backtest the strategy
   - View performance metrics

## Example Strategies

### Simple RSI Strategy

```
Buy BTC when RSI(14) falls below 30 on a 4h timeframe, sell when RSI goes above 70
```

### Moving Average Crossover with Volume

```
Buy ETH when the 20-day EMA crosses above the 50-day EMA with volume increasing, sell when price drops 5% from peak
```

### MACD and Bollinger Bands

```
Buy ADA when MACD shows bullish crossover and price is below lower Bollinger Band (20,2), exit when price touches upper Bollinger Band
```

## Production Deployment

For production deployment, consider the following:

1. **API Key Security**: Store API keys in a secure location using environment variables or a secrets manager
2. **Rate Limiting**: Implement API rate limiting to prevent excessive API calls
3. **Monitoring**: Add comprehensive logging and monitoring
4. **Authentication**: Add user authentication for public-facing deployments
5. **Cloud Deployment**: Deploy to AWS, Azure, or Google Cloud with proper scaling

### AWS Deployment Example

```bash
# Build and push Docker image to ECR
aws ecr create-repository --repository-name crypto-strategy-generator
docker build -t <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com/crypto-strategy-generator:latest .
aws ecr get-login-password | docker login --username AWS --password-stdin <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com
docker push <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com/crypto-strategy-generator:latest

# Deploy to ECS or Fargate
# Follow AWS documentation for detailed steps
```

## Troubleshooting

### Common Issues

1. **Missing Modules**: If you encounter "No module named X", make sure you've installed all dependencies with `pip install -r requirements.txt`

   - **Note about module names**: Some packages use different names for pip installation versus Python imports:
     - `python-dotenv` package → `import dotenv`
     - `rpds-py` package → `import rpds`

2. **API Connection Issues**: Check your API keys and internet connection

3. **No Trading Signals**: Try relaxing your strategy conditions (e.g., RSI < 40 instead of RSI < 30)

4. **Error with rpds-py**: If you encounter issues with rpds-py, reinstall with `pip install --force-reinstall rpds-py`

5. **Module import failures**: The application includes an `import_test.py` script to verify all required modules can be imported. Run it to diagnose import issues:

   ```bash
   python import_test.py
   ```

## Architecture

The application consists of the following main components:

- **NLP Handler** (`app/nlp_handler.py`): Interprets natural language strategy descriptions using Azure OpenAI
- **Strategy Generator** (`app/strategy_generator.py`): Generates executable Python code from strategy parameters
- **Data Handler** (`app/data_handler.py`): Fetches historical cryptocurrency data from Binance
- **Backtester** (`app/backtester.py`): Executes and evaluates trading strategies against historical data
- **UI** (`main.py`): Streamlit interface for interacting with the system

## Testing

Run the test suite to ensure all components are working properly:

```bash
python tests/run_tests.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the interactive web interface
- [Azure OpenAI](https://azure.microsoft.com/services/cognitive-services/openai-service/) for NLP capabilities
- [pandas-ta](https://github.com/twopirllc/pandas-ta) for technical analysis indicators
- [Binance API](https://github.com/binance/binance-spot-api-docs) for market data
