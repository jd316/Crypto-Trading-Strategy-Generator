#!/bin/bash

echo "Starting Crypto Trading Strategy Generator..."
echo "==========================================="

# Check platform for specific dependencies
platform=$(uname)
if [ "$platform" = "Darwin" ]; then
    echo "macOS detected - checking for TA-Lib..."
    # Check if TA-Lib is installed via Homebrew
    if ! brew list ta-lib &>/dev/null; then
        echo "TA-Lib not found. Do you want to install it with Homebrew? (y/n)"
        read -p "> " install_talib
        if [ "$install_talib" = "y" ] || [ "$install_talib" = "Y" ]; then
            brew install ta-lib
        else
            echo "Note: TA-Lib is required for some indicators. You may have issues with certain strategies."
        fi
    else
        echo "TA-Lib installation found."
    fi
elif [ "$platform" = "Linux" ]; then
    echo "Linux detected - checking for build dependencies..."
    # This is simplified and might need adjustment for different Linux distros
    if [ -f /etc/debian_version ]; then
        echo "Debian/Ubuntu detected. Do you want to install build dependencies? (y/n)"
        read -p "> " install_deps
        if [ "$install_deps" = "y" ] || [ "$install_deps" = "Y" ]; then
            sudo apt-get update
            sudo apt-get install -y build-essential libssl-dev
        fi
    else
        echo "Note: You may need to install build-essential and libssl-dev packages if you encounter cryptography build errors."
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        echo "Please make sure Python 3.8+ is installed."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Warning: Some dependencies may not have installed correctly."
    sleep 3
fi

# Run the import test to verify modules
echo "Testing module imports..."
python import_test.py
if [ $? -ne 0 ]; then
    echo "Some imports failed. Attempting to fix..."
    pip install python-dotenv rpds-py
    echo "Retesting imports..."
    python import_test.py
fi

# Run the Streamlit app
echo "Starting Streamlit application..."
streamlit run main.py

echo "Application closed."
read -p "Press Enter to exit..." 