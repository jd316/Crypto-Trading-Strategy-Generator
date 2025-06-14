import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_TESTNET_SECRET_KEY")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") 
AZURE_OPENAI_API_KEY = os.getenv("AZURE_API_KEY")