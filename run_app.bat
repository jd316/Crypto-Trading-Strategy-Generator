@echo off
ECHO Starting Crypto Trading Strategy Generator...
ECHO =========================================

REM Check if virtual environment exists
IF NOT EXIST venv (
    ECHO Creating Python virtual environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Failed to create virtual environment.
        ECHO Please make sure Python 3.8+ is installed.
        PAUSE
        EXIT /B 1
    )
)

REM Activate virtual environment
CALL venv\Scripts\activate

REM Install dependencies
ECHO Installing/updating dependencies...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    ECHO Warning: Some dependencies may not have installed correctly.
    TIMEOUT /T 3
)

REM Run the import test to verify modules
ECHO Testing module imports...
python import_test.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO Some imports failed. Attempting to fix...
    pip install python-dotenv rpds-py
    ECHO Retesting imports...
    python import_test.py
)

REM Run the Streamlit app
ECHO Starting Streamlit application...
streamlit run main.py

ECHO Application closed.
PAUSE 