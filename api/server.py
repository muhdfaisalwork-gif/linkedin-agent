"""
GitHub SEO Agent — FastAPI Web Server
Provides REST API endpoints for repository auditing, README generation,
multi-channel launch packs, and community health file installation.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from core.seo_engine import GitHubSEOAgent

app = FastAPI(
    title="GitHub SEO Agent",
    description="Open-Source Repository Discoverability Engine",
    version="1.0.0"
)

# Automatically load .env if present
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

REPO_DIR = os.getenv("REPO_DIR", os.getcwd())
REPO_OWNER = os.getenv("REPO_OWNER", "owner")
REPO_NAME = os.getenv("REPO_NAME", "repo")

engine = GitHubSEOAgent(REPO_OWNER, REPO_NAME, repo_dir=REPO_DIR)


# ─── Pydantic Models ───────────────────────────────────────────────

class ReadmeRequest(BaseModel):
    project_name: str
    tagline: str = "An awesome open-source project"
    features: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    apply: bool = False

class LaunchRequest(BaseModel):
    channel: str = "all"

class AILaunchRequest(BaseModel):
    channel: str = "hacker_news"
    angle: Optional[str] = None
    model: Optional[str] = None
    repo_url: Optional[str] = None
    project_name: Optional[str] = None
    features: Optional[List[str]] = None

class CommunityRequest(BaseModel):
    apply: bool = False


# ─── Endpoints ──────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "github-seo-agent", "version": "1.0.0"}

@app.get("/api/audit")
def run_audit():
    """Runs SEO audit on the configured repository directory."""
    try:
        return engine.audit_repository()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/readme")
def generate_readme(req: ReadmeRequest):
    """Generates an SEO-optimized README template."""
    try:
        features = req.features or ["Feature 1"]
        tech = req.tech_stack or ["Python"]
        content = engine.generate_optimized_readme(req.project_name, req.tagline, features, tech)
        applied = False
        if req.apply:
            readme_path = os.path.join(engine.repo_dir or ".", "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)
            applied = True
        return {"status": "success", "applied": applied, "readme_content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/launch")
def generate_launch(req: LaunchRequest):
    """Generates multi-channel launch copy from curated templates."""
    try:
        packs = engine.generate_launch_pack(channel=req.channel)
        return {"status": "success", "channel": req.channel, "packs": packs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-launch")
def ai_synthesized_launch(req: AILaunchRequest):
    """Generates AI-crafted launch copy using OpenRouter free models, with fallback to curated template."""
    try:
        from core.ai_synthesizer import AISynthesizer
        synth = AISynthesizer(model=req.model or "google/gemma-4-31b-it:free")
        repo_url = req.repo_url or f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        features = req.features or ["open-source"]
        res = synth.synthesize_launch_copy(repo_url, req.project_name or REPO_NAME, features, req.channel, req.angle or "")
        
        # If OpenRouter returned an error (e.g. rate limit/timeout), gracefully fallback to curated template
        if "result" in res and res["result"]:
            return {"status": "success", "channel": req.channel, "source": "openrouter_ai", "result": res["result"], "model_used": res.get("model_used")}
        
        packs = engine.generate_launch_pack(channel=req.channel)
        fallback_text = packs.get(req.channel) or (list(packs.values())[0] if packs else "")
        return {
            "status": "success",
            "channel": req.channel,
            "source": "curated_fallback",
            "result": fallback_text,
            "note": f"Served via curated launch pack (AI fallback: {res.get('error', 'unknown')})"
        }
    except Exception as e:
        packs = engine.generate_launch_pack(channel=req.channel)
        fallback_text = packs.get(req.channel) or (list(packs.values())[0] if packs else "")
        return {
            "status": "success",
            "channel": req.channel,
            "source": "curated_fallback",
            "result": fallback_text,
            "note": f"Served via curated launch pack (Exception: {str(e)})"
        }

@app.post("/api/community")
def install_community(req: CommunityRequest):
    """Generates GitHub Community Standards files."""
    try:
        files = engine.generate_community_health_files()
        if req.apply and engine.repo_dir:
            written = []
            for rel_path, content in files.items():
                full_path = os.path.join(engine.repo_dir, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                written.append(rel_path)
            return {"status": "success", "applied": True, "files_written": written}
        return {"status": "success", "applied": False, "files": list(files.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Static & Web Dashboard ──────────────────────────────────────────

from fastapi.responses import FileResponse

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "GitHub SEO Agent API"}

try:
    if os.path.exists(static_dir):
        from fastapi.staticfiles import StaticFiles
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception:
    pass
