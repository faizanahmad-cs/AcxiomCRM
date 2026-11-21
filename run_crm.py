import sys
import subprocess
import time
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_api(port=8000):
    print(f"🚀 Starting AcxiomCRM REST API on http://127.0.0.1:{port} (Swagger docs: http://127.0.0.1:{port}/docs)...")
    cmd = [sys.executable, "-m", "uvicorn", "acxiom_crm.backend.api.main:app", "--host", "127.0.0.1", "--port", str(port)]
    return subprocess.Popen(cmd)

def run_ui(port=8501):
    print(f"✨ Starting AcxiomCRM Streamlit UI on http://localhost:{port}...")
    ui_script = BASE_DIR / "acxiom_crm" / "frontend" / "app.py"
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(ui_script),
        "--server.port", str(port),
        "--server.headless", "true",
        "--theme.base", "dark"
    ]
    return subprocess.Popen(cmd)

def main():
    parser = argparse.ArgumentParser(description="AcxiomCRM Server & UI Runner")
    parser.add_argument("--api-only", action="store_true", help="Launch only FastAPI REST API")
    parser.add_argument("--ui-only", action="store_true", help="Launch only Streamlit Frontend")
    parser.add_argument("--api-port", type=int, default=8000, help="Port for FastAPI backend")
    parser.add_argument("--ui-port", type=int, default=8501, help="Port for Streamlit UI")
    args = parser.parse_args()

    print("=" * 65)
    print("           💼 AcxiomCRM Enterprise System")
    print("  Customer-Sales Lifecycle, RBAC, Validation & Auditing")
    print("=" * 65)
    print("Default Demo Accounts:")
    print("  👑 Admin:           admin@acxiomcrm.com    / Admin@12345")
    print("  👔 Manager:         manager@acxiomcrm.com  / Manager@12345")
    print("  💼 Sales Executive: sales1@acxiomcrm.com   / Sales@12345")
    print("  💼 Sales Executive: sales2@acxiomcrm.com   / Sales@12345")
    print("=" * 65)

    processes = []
    try:
        if args.api_only:
            p_api = run_api(args.api_port)
            processes.append(p_api)
            p_api.wait()
        elif args.ui_only:
            p_ui = run_ui(args.ui_port)
            processes.append(p_ui)
            p_ui.wait()
        else:
            p_api = run_api(args.api_port)
            processes.append(p_api)
            time.sleep(2)  # Give API a moment to start
            p_ui = run_ui(args.ui_port)
            processes.append(p_ui)

            print("\n✅ System is fully operational!")
            print(f"  👉 Streamlit Web App: http://localhost:{args.ui_port}")
            print(f"  👉 FastAPI REST Docs: http://localhost:{args.api_port}/docs\n")
            print("Press Ctrl+C to terminate both servers.\n")

            while True:
                time.sleep(1)
                for p in processes:
                    if p.poll() is not None:
                        return
    except KeyboardInterrupt:
        print("\nShutting down AcxiomCRM services...")
    finally:
        for p in processes:
            if p.poll() is None:
                p.terminate()

if __name__ == "__main__":
    main()
