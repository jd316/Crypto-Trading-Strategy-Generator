import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def interpret_trading_strategy(user_input: str) -> dict:
    """
    Parse a user's trading strategy input and extract key parameters.
    This is a fallback function that doesn't require OpenAI API.
    
    Args:
        user_input: Natural language description of trading strategy
        
    Returns:
        dict: Extracted strategy parameters
    """
    logger.info(f"Processing strategy: {user_input}")
    
    # Default values
    strategy = {
        "Asset": "BTC/USDT",
        "Entry Condition": ["RSI(14) < 30"],
        "Exit Condition": ["Take profit at 5%", "Stop loss at 2%"],
        "Entry Indicators": ["RSI"],
        "Exit Indicators": ["Take Profit", "Stop Loss"],
        "Actions": ["Buy", "Sell"],
        "Timeframe": "1H",
        "Amount": "1"
    }
    
    # Crude keyword matching for basic understanding
    if "ETH" in user_input.upper():
        strategy["Asset"] = "ETH/USDT"
    elif "BNB" in user_input.upper():
        strategy["Asset"] = "BNB/USDT"
        
    if "15M" in user_input.upper() or "15 MIN" in user_input.upper():
        strategy["Timeframe"] = "15M"
    elif "4H" in user_input.upper() or "4 HOUR" in user_input.upper():
        strategy["Timeframe"] = "4H"
    elif "1D" in user_input.upper() or "DAILY" in user_input.upper():
        strategy["Timeframe"] = "1D"
    
    if "MACD" in user_input.upper():
        strategy["Entry Indicators"].append("MACD")
    if "EMA" in user_input.upper():
        strategy["Entry Indicators"].append("EMA")
    if "SMA" in user_input.upper():
        strategy["Entry Indicators"].append("SMA")
    
    logger.info(f"Extracted strategy: {strategy}")
    return strategy

def generate_trading_strategy(strategy_data: dict) -> str:
    """
    Generate a trading strategy code based on parameters.
    This is a fallback function that doesn't require OpenAI API.
    
    Args:
        strategy_data: Dictionary containing strategy parameters
        
    Returns:
        str: Generated strategy code
    """
    asset = strategy_data.get("Asset", "BTC/USDT")
    timeframe = strategy_data.get("Timeframe", "1H")
    entry_indicators = strategy_data.get("Entry Indicators", ["RSI"])
    
    # Simple template for RSI strategy
    code = f"""import pandas as pd
import pandas_ta as ta
import numpy as np

def trading_strategy(ohlc_data):
    # Make a copy of the dataframe to avoid modifying the original
    df = ohlc_data.copy()
    
    # Calculate indicators for {asset} on {timeframe} timeframe
"""
    
    # Add indicators based on strategy
    if "RSI" in entry_indicators:
        code += """    # Calculate RSI
    df.ta.rsi(length=14, append=True)
    
    # Initialize signal column
    df['signal'] = 0
    
    # Generate signals
    df.loc[df['RSI_14'] < 30, 'signal'] = 1  # Buy signal
    df.loc[df['RSI_14'] > 70, 'signal'] = -1  # Sell signal
"""
    
    if "MACD" in entry_indicators:
        code += """    # Calculate MACD
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    # Generate MACD crossover signals
    df['macd_crossover'] = np.where(df['MACDh_12_26_9'] > 0, 1, 0)
    df.loc[(df['MACDh_12_26_9'] > 0) & (df['MACDh_12_26_9'].shift(1) < 0), 'signal'] = 1  # Buy on crossover
"""
    
    # Add standard return statement
    code += """    
    # Forward fill NaN values in the signal column
    df['signal'] = df['signal'].fillna(0)
    
    return df
"""
    
    return code

if __name__ == "__main__":
    # Test the strategy interpreter
    test_strategy = "Buy BTC when RSI is below 30 on the 4H timeframe and sell when RSI is above 70"
    strategy_params = interpret_trading_strategy(test_strategy)
    print(json.dumps(strategy_params, indent=2))
    
    # Test the strategy generator
    generated_code = generate_trading_strategy(strategy_params)
    print("\nGenerated Strategy Code:")
    print(generated_code)