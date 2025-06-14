#!/usr/bin/env python
"""
Dependency checker for Crypto Trading Strategy Generator
This script verifies all required dependencies are installed and
installs missing packages if needed.
"""
import sys
import os
import subprocess
import importlib
import pkg_resources

def print_status(message, status="info"):
    """Print a status message with color."""
    colors = {
        "info": "\033[94m",  # Blue
        "success": "\033[92m",  # Green
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "reset": "\033[0m"    # Reset
    }
    
    print(f"{colors.get(status, colors['info'])}{message}{colors['reset']}")

def is_venv():
    """Check if running in a virtual environment."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def install_package(package_name):
    """Install a Python package using pip."""
    try:
        print_status(f"Installing {package_name}...", "info")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print_status(f"Failed to install {package_name}", "error")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    requirements = [
        "streamlit>=1.25.0",
        "openai>=0.27.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "python-dotenv>=0.21.0",
        "python-binance>=0.7.9",
        "pandas-ta>=0.3.14b0",
        "rpds-py>=0.10.0",
        "cryptography>=39.0.0",
        "aiohttp>=3.8.0"
    ]
    
    # Convert requirements strings to package names
    packages = {}
    for req in requirements:
        package = req.split(">=")[0]
        version = req.split(">=")[1] if ">=" in req else None
        packages[package] = version
    
    missing_packages = []
    for package, version in packages.items():
        # Convert package name for import
        import_name = package.replace("-", "_")
        
        try:
            importlib.import_module(import_name)
            print_status(f"✓ {package} - OK", "success")
        except ImportError:
            print_status(f"✗ {package} - Missing", "error")
            missing_packages.append(package)
    
    if missing_packages:
        print_status("\nMissing packages detected!", "warning")
        if not is_venv():
            print_status("WARNING: Not running in a virtual environment. It's recommended to use a virtual environment.", "warning")
        
        install = input("\nDo you want to install missing packages? (y/n): ").lower().strip()
        if install == 'y':
            for package in missing_packages:
                install_package(package)
                # Verify installation
                try:
                    import_name = package.replace("-", "_")
                    importlib.import_module(import_name)
                    print_status(f"✓ {package} successfully installed", "success")
                except ImportError:
                    print_status(f"✗ {package} installation verification failed", "error")
                    return False
            return True
        else:
            print_status("Please install the missing packages manually with:", "info")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    print_status("\nAll dependencies are installed!", "success")
    return True

if __name__ == "__main__":
    print_status("Checking dependencies for Crypto Trading Strategy Generator...", "info")
    if check_dependencies():
        print_status("\nAll dependencies are installed. You can run the application with:", "success")
        print_status("streamlit run main.py", "info")
    else:
        print_status("\nPlease install all required dependencies before running the application.", "error") 