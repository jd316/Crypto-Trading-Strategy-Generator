"""
Import tester for Crypto Trading Strategy Generator
This script checks if all required dependencies can be imported.
"""
import sys
import os
import importlib

def print_status(message, success=True):
    """Print a status message with color."""
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")

def check_imports():
    """Check if all required modules can be imported."""
    required_modules = [
        "streamlit",
        "openai",
        "pandas",
        "numpy",
        "requests",
        "dotenv",
        "pandas_ta",
        "rpds",
        "cryptography",
        "aiohttp"
    ]
    
    # Map pip package names to import names
    package_to_import = {
        "python-dotenv": "dotenv",
        "rpds-py": "rpds"
    }
    
    # Map import names back to pip package names for error messages
    import_to_package = {v: k for k, v in package_to_import.items()}
    
    success = True
    for module in required_modules:
        try:
            # Try to import the module
            importlib.import_module(module)
            # Get the pip package name for display
            package = import_to_package.get(module, module)
            print_status(f"{package} successfully imported")
        except ImportError as e:
            package = import_to_package.get(module, module)
            print_status(f"{package} import failed: {e}", False)
            success = False
    
    if success:
        print("\nAll imports successful!")
    else:
        print("\nSome imports failed. This might cause the application to fail.")
    
    # Print Python import path for debugging
    print("\nPython sys.path:")
    for path in sys.path:
        print(f"  {path}")
        
    return success

if __name__ == "__main__":
    print("Testing imports for Crypto Trading Strategy Generator...\n")
    check_imports() 