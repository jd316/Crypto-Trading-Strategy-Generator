@echo off
echo ===================================
echo Crypto Trading Strategy Generator
echo ===================================

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7+.
    exit /b 1
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Using system Python.
)

REM Check dependencies
echo Checking dependencies...
python check_deps.py

REM Start the application if dependencies check passed
if %ERRORLEVEL% equ 0 (
    echo Starting Crypto Trading Strategy Generator...
    python -m streamlit run main.py
) else (
    echo Failed to verify dependencies. Please install required packages manually.
    echo pip install -r requirements.txt
    exit /b 1
) 