"""
AcxiomCRM - Streamlit Frontend Application
Run via:
    streamlit run app.py
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute the main Streamlit application
from acxiom_crm.frontend import app
