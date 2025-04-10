"""
Main entry point for the Grade Analysis Tool GUI Application.
Imports and runs the main application class.
"""

# Ensure the main package directory is in the path if running this script directly
import os
import sys

# Add the parent directory (Comp330) to sys.path to find GoodAndBadList etc.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Make sure test_gui module is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the function to run the app from the app module using absolute import
from test_gui.app import run_app

# Verify scipy is available for z-test functionality
try:
    import scipy.stats
except ImportError:
    print("Warning: scipy not found. Z-test functionality will be limited.")
    print("Install scipy with: pip install scipy")

# Run the application when the script is executed directly
if __name__ == "__main__":
    run_app()
