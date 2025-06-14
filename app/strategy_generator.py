import os
import logging
import pandas as pd
import pandas_ta as ta
import requests
import json
from app.data_handler import fetch_ohlc_data  # Ensure proper import
from openai import AzureOpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)

# Azure OpenAI setup
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://btcla-m71runj2-northcentralus.services.ai.azure.com/models")
api_key = os.getenv("AZURE_API_KEY")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
api_version = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")

class StrategyGenerator:
    def __init__(self, strategy_data):
        self.strategy_data = strategy_data
        self.asset = strategy_data.get("Asset", "BTC")
        self.timeframe = strategy_data.get("Timeframe", "1H")
        self.amount = strategy_data.get("Amount", "1")
        self.entry_conditions = strategy_data.get("Entry Condition", [])
        self.exit_conditions = strategy_data.get("Exit Condition", [])
        
        # Fetch OHLCV data dynamically if needed
        try:
            self.ohlcv_data = fetch_ohlc_data(self.asset, self.timeframe)
        except Exception as e:
            logging.error(f"Error fetching OHLCV data: {e}")
            self.ohlcv_data = pd.DataFrame()

    def generate_strategy(self):
        """Generates trading strategy code using Azure OpenAI."""
        
        # Convert fetched OHLCV data to a sample format for GPT understanding
        sample_ohlcv = self.ohlcv_data.head(3).to_dict() if isinstance(self.ohlcv_data, pd.DataFrame) and not self.ohlcv_data.empty else {}

        # Concise system and user prompts to avoid token limits
        system_message = (
            "You are an expert quant trader. Generate a fully executable Python function named `trading_strategy(ohlc_data)` "
            "that returns a DataFrame with original columns and integer `signal` column (1 buy, -1 sell, 0 no action). "
            "Use pandas-ta for indicators, convert numeric types, and vectorize operations. Relax strict entry/exit conditions to increase signals. "
            "Output only code, no explanations."
        )
        user_message = f"Asset: {self.asset}\nTimeframe: {self.timeframe}\nEntry Conditions: {self.entry_conditions}\nExit Conditions: {self.exit_conditions}\nSample OHLCV: {sample_ohlcv}\nGenerate code now."

        # Check if Azure OpenAI is properly configured
        if not endpoint or not api_key:
            error_msg = "Azure OpenAI configuration is missing. This is required for production use."
            logging.error(error_msg)
            raise RuntimeError(error_msg)
            
        try:
            # Instantiate Azure SDK client and fetch strategy code
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_version=api_version,
                api_key=api_key
            )
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_completion_tokens=2000,
                model=deployment_name
            )
            # Extract and clean the generated code
            generated_code = response.choices[0].message.content.strip()
            generated_code = generated_code.replace("```python", "").replace("```", "").strip()
            # Validate output
            if not generated_code:
                error_msg = "Generated code is empty. Azure OpenAI did not provide a valid response."
                logging.error(error_msg)
                raise ValueError(error_msg)
            logging.info("Generated Code: %s", generated_code[:100] + "...")
            return generated_code
        except Exception as e:
            error_msg = f"Azure OpenAI API request failed: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)