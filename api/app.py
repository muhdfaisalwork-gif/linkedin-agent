import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from core.db.database import init_db
from core.scheduler.agent_runner import AutonomousAgentRunner

from api.routes import posts, profile, brain, comments, inbox, analytics, settings, planner

runner = AutonomousAgentRunner(check_interval_seconds=60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and load persisted settings
    init_db()
    try:
        from core.db.database import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT key, value FROM settings")
        for k, v in c.fetchall():
            if v and not os.getenv(k):
                os.environ[k] = v
        conn.close()
    except Exception:
        pass
    runner.start()
    yield
    # Shutdown: stop scheduler
    runner.stop()

app = FastAPI(
    title="NexusAgent - Autonomous LinkedIn Studio",
    description="Open-Source Autonomous LinkedIn Agent with Evolving Brain and 82-Rule Writing Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(posts.router)
app.include_router(profile.router)
app.include_router(brain.router)
app.include_router(comments.router)
app.include_router(inbox.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(planner.router)

# Mount static and storage folders
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
STORAGE_IMAGES_DIR = os.path.join(BASE_DIR, "storage", "images")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(STORAGE_IMAGES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/storage/images", StaticFiles(directory=STORAGE_IMAGES_DIR), name="storage_images")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "NexusAgent Studio API running. Open /static/index.html"}
