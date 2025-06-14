import json
import os
import re
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up the Azure OpenAI endpoint and key
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://btcla-m71runj2-northcentralus.services.ai.azure.com/models")
api_key = os.getenv("AZURE_API_KEY")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
api_version = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")

def interpret_user_input(user_input):
    """
    Use Azure OpenAI to interpret user input and extract strategy parameters.
    :param user_input: Natural language input from the user
    :return: Dictionary containing extracted strategy parameters
    """
    # Build detailed prompt for strategy interpretation
    prompt = f"""
    Extract the following details from the user's trading strategy input and return a JSON object ONLY:
    - Asset (e.g., BTC, ETH)
    - Entry Condition (e.g., Buy when RSI > 30)
    - Exit Condition (e.g., Sell when RSI > 70)
    - Entry Indicators (e.g., RSI, Moving Averages)
    - Exit Indicators (e.g., Trailing stop loss, stop loss)
    - Actions (e.g., buy, sell)
    - Timeframe (e.g., 1d, 1h, 1m)
    - Amount (if mentioned)

    User Input: {user_input}

    Return only a JSON object.
    """

    # Check if Azure OpenAI is properly configured
    if not endpoint or not api_key:
        error_msg = "Azure OpenAI configuration is missing. This is required for production use."
        logging.error(error_msg)
        raise RuntimeError(error_msg)

    try:
        # Direct HTTP request to Azure OpenAI
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        payload = {
            "messages": [
                {"role": "system", "content": "You are a trading strategy interpreter."},
                {"role": "user", "content": prompt}
            ],
            "max_completion_tokens": 512,
            "temperature": 1
        }
        base_endpoint = endpoint.replace("/models", "")
        api_url = f"{base_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        logging.info(f"Making Azure OpenAI API request to: {api_url}")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            error_msg = f"Azure OpenAI API error: {response.status_code}, {response.text}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        response_data = response.json()
        raw_output = response_data["choices"][0]["message"]["content"]
        logging.info(f"Raw Azure OpenAI Response: {raw_output}")

        # Extract JSON using regex in case of additional text
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if match:
            json_output = match.group(0)  # Extract only the JSON part
            try:
                return json.loads(json_output)
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON response: {e}"
                logging.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = "No valid JSON found in Azure OpenAI response."
            logging.error(error_msg)
            raise ValueError(error_msg)

    except requests.exceptions.RequestException as e:
        error_msg = f"Network error connecting to Azure OpenAI: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Azure OpenAI API request failed: {e}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
