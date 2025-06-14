#!/bin/bash
set -e

echo "==================================="
echo "Crypto Trading Strategy Generator"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.7+."
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Using system Python."
fi

# Check dependencies
echo "Checking dependencies..."
python3 check_deps.py

# Start the application if dependencies check passed
if [ $? -eq 0 ]; then
    echo "Starting Crypto Trading Strategy Generator..."
    python3 -m streamlit run main.py
else
    echo "Failed to verify dependencies. Please install required packages manually."
    echo "pip install -r requirements.txt"
    exit 1
fi 