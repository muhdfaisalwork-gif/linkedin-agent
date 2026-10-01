import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from core.seo.github_seo import LinkedInNexusGitHubSEO

router = APIRouter(prefix="/api/seo", tags=["seo"])
engine = LinkedInNexusGitHubSEO()

class OptimizeReadmeRequest(BaseModel):
    apply: bool = False

class LaunchPackRequest(BaseModel):
    channel: str = "all"

class AILaunchRequest(BaseModel):
    channel: str = "hacker_news"
    angle: Optional[str] = None
    model: Optional[str] = None

class AIPitchRequest(BaseModel):
    focus_area: str = "developer_acquisition"
    model: Optional[str] = None

@router.get("/audit")
def get_seo_audit():
    """Returns repository GitHub SEO health score (0-100), checklist, and recommended topics."""
    try:
        return engine.audit_repository()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-readme")
def optimize_readme(req: OptimizeReadmeRequest):
    """Generates search-optimized README for LinkedIn Nexus Agent, with optional write-to-disk."""
    try:
        content = engine.generate_optimized_readme()
        applied = False
        if req.apply:
            readme_path = os.path.join(engine.repo_dir, "README.md")
            backup_path = os.path.join(engine.repo_dir, "README.md.backup")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    with open(backup_path, "w", encoding="utf-8") as b:
                        b.write(f.read())
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)
            applied = True

        return {
            "status": "success",
            "applied": applied,
            "readme_content": content,
            "byte_count": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/launch-pack")
def get_launch_pack(req: LaunchPackRequest):
    """Generates tailored launch copy for Hacker News, Reddit, Twitter, and GitHub Releases."""
    try:
        packs = engine.generate_launch_pack(channel=req.channel)
        return {
            "status": "success",
            "channel": req.channel,
            "packs": packs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/install-community-files")
def install_community_files():
    """Generates .github workflows, issue templates, CONTRIBUTING.md, and SECURITY.md."""
    try:
        return engine.generate_community_health_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-launch")
def generate_ai_launch(req: AILaunchRequest):
    """Generates AI-crafted launch copy using OpenRouter free models (Gemma 4, Nemotron)."""
    try:
        return engine.generate_ai_launch_content(
            channel=req.channel,
            angle=req.angle or "",
            model=req.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-pitch")
def generate_ai_pitch(req: AIPitchRequest):
    """Generates punchy README pitch hero copy using OpenRouter free models."""
    try:
        return engine.ai_pitch_readme(
            focus_area=req.focus_area,
            model=req.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
