"""
AcxiomCRM - FastAPI REST API Backend
Run via:
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from acxiom_crm.backend.api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
