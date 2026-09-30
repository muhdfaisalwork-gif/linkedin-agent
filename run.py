import os
import sys
import webbrowser
import threading
import time
import uvicorn
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Prevent cp1252 charmap encoding errors on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

from core.db.database import init_db

def open_browser(port: int):
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{port}")

def main():
    print("=" * 65)
    print("  [LinkedIn Nexus Agent] Autonomous AI Studio & Dashboard")
    print("  [Brain] Cognitive Brain: Story Bank, Voice Profile & Heuristics")
    print("  [Engine] Writing Engine: 82-Rule Strict Human-Natural Gate")
    print("=" * 65)

    # Initialize Database and Seeds
    print("\n[1/3] Initializing SQLite database and seeding Story Bank...")
    init_db()
    print("      [OK] Story Bank seeded with Sultrix, Shadow Stream, Shadow Voice, CRM, & Raulf Int.")

    # Port and host
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")

    print(f"\n[2/3] Launching Web Dashboard at http://localhost:{port}...")
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    print("\n[3/3] Starting LinkedIn Nexus Agent Studio Server...")
    uvicorn.run("api.app:app", host=host, port=port, log_level="info", reload=False)

if __name__ == "__main__":
    main()
