import requests
import pandas as pd
import logging
import os
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client

# Set up logging
logging.basicConfig(level=logging.INFO)

# Try to import Binance client if available
try:
    from app.config import BINANCE_API_KEY, BINANCE_SECRET_KEY
    
    # Initialize client with error handling
    try:
        client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        logging.info("Binance client initialized successfully")
        BINANCE_AVAILABLE = True
    except Exception as e:
        logging.error(f"Failed to initialize Binance client: {e}")
        client = None
        BINANCE_AVAILABLE = False
except ImportError:
    logging.error("Binance client not available - this is required for production use")
    client = None
    BINANCE_AVAILABLE = False

def preprocess_symbol(symbol):
    """
    Preprocess the symbol to match Binance API format.
    :param symbol: Trading pair (e.g., ETH, ETH/USDT, BTCUSDT)
    :return: Formatted symbol (e.g., ETHUSDT)
    """
    symbol = symbol.upper().replace("/", "")
    if not symbol.endswith('USDT'):
        symbol += 'USDT'
    return symbol

def fetch_ohlc_data(symbol, interval=None):
    """
    Fetch OHLC data for a given symbol and interval.
    Defaults to '1H' if no interval is provided.
    """
    interval_mapping = {
        '1H': '1h',
        '4H': '4h',
        '1D': '1d',
        '1W': '1w',
        '1M': '1M',
        '15M': '15m',
        '30M': '30m',
    }

    symbol = preprocess_symbol(symbol)

    # ✅ Fixed interval validation and mapping
    original_interval = interval
    interval = interval.upper() if interval else None
    if interval not in interval_mapping:
        logging.warning(f"Invalid or missing interval '{original_interval}'. Defaulting to '1H'.")
        interval = '1H'  # Use the key from interval_mapping
    binance_interval = interval_mapping[interval]

    # Verify Binance client availability
    if not BINANCE_AVAILABLE or client is None:
        error_msg = "Binance API client is not available. This is required for production use."
        logging.error(error_msg)
        raise RuntimeError(error_msg)

    try:
        # Fetch 3 months of data
        klines = client.get_historical_klines(symbol, binance_interval, "3 months ago UTC")
        if not klines:
            error_msg = f"No data returned from Binance for {symbol} with interval {interval}"
            logging.error(error_msg)
            raise ValueError(error_msg)

        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                        'close_time', 'quote_asset_volume', 'number_of_trades', 
                                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Get only required columns
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        # Ensure numeric data types for all price and volume columns
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Check for and handle NaN values
        if df.isna().any().any():
            logging.warning(f"NaN values found in data for {symbol}. Handling them appropriately.")
            # Forward fill NaN values where possible
            df = df.ffill()
            # If any NaN values remain at the beginning, backward fill
            df = df.bfill()
            
        # Verify we have sufficient data
        if len(df) < 20:  # Minimum data required for most indicators
            error_msg = f"Insufficient data points ({len(df)}) returned for {symbol}. At least 20 are required."
            logging.error(error_msg)
            raise ValueError(error_msg)
            
        return df

    except Exception as e:
        error_msg = f"Failed to fetch data for {symbol} with interval {interval} from Binance. Error: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)

def is_asset_available(symbol):
    """
    Check if the asset is available on Binance.
    :param symbol: Trading pair (e.g., BTCUSDT)
    :return: True if available, False otherwise
    """
    if not BINANCE_AVAILABLE:
        error_msg = "Binance API is not available. Cannot verify asset availability."
        logging.error(error_msg)
        raise RuntimeError(error_msg)
        
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url, timeout=10)  # Add timeout for production safety
        
        if response.status_code != 200:
            error_msg = f"Failed to get exchange info from Binance API. Status code: {response.status_code}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
            
        exchange_info = response.json()
        symbols = [s['symbol'] for s in exchange_info['symbols']]
        
        formatted_symbol = preprocess_symbol(symbol)
        is_available = formatted_symbol in symbols
        
        if not is_available:
            logging.warning(f"Symbol {formatted_symbol} is not available on Binance")
        
        return is_available
        
    except Exception as e:
        error_msg = f"Error checking asset availability: {e}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)