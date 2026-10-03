import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from core.reach.feed_engine import ReachFeedEngine
from core.linkedin.browser_agent import LinkedInBrowserAgent
from core.reach.vision_analyzer import ReachVisionAnalyzer
from core.llm.client import UniversalLLMClient
from core.brain.brain import BrainManager

router = APIRouter(prefix="/api/reach", tags=["reach"])

browser_agent = LinkedInBrowserAgent()
feed_engine = ReachFeedEngine(browser_agent=browser_agent)
llm = UniversalLLMClient()
vision_analyzer = ReachVisionAnalyzer(llm_client=llm)
brain = BrainManager()

class InspectRequest(BaseModel):
    url: str

class LikeRequest(BaseModel):
    post_urn: str

class VisionAnalyzeRequest(BaseModel):
    image_url: Optional[str] = None
    prompt: Optional[str] = None

@router.post("/scan-feed")
def scan_feed():
    """Triggers autonomous browser visual scan of the LinkedIn Feed."""
    return feed_engine.scan_and_log_feed(limit=10)

@router.get("/feed")
def get_scanned_feed(limit: int = 20):
    """Returns previously scanned posts from the SQLite database."""
    posts = feed_engine.get_recent_scanned_posts(limit=limit)
    return {"posts": posts, "count": len(posts)}

@router.post("/inspect")
def inspect_url(req: InspectRequest):
    """
    Inspects any URL (LinkedIn profile, post, or article) via dual-backend
    (Jina Reader + Browser DOM) and generates strategic founder commentary angles.
    """
    clean_url = (req.url or "").strip()
    if not clean_url or clean_url.lower() in ("http://", "https://"):
        return {"status": "error", "message": "A valid URL is required for inspection."}

    res = feed_engine.inspect_url(clean_url)
    if res.get("status") != "success":
        return res

    content = res.get("content", "")
    title = res.get("title", "")

    # Enrich with Brain analysis & response angles
    knowledge = brain.get_context_for_generation("LinkedIn Post / Article Reaction")
    prompt = f"""You are the strategic brain of LinkedIn Nexus Agent.
Analyze this inspected article/post and generate:
1. Executive Summary (2 sentences)
2. Core Argument / Thesis
3. Strategic Contrarian or Founder Angle (how the user can comment on this using their background in high-performance trading systems, video streaming, or AI agents)
4. Recommended 1-Sentence Opening Hook for a reply

Extracted Title: {title}
Extracted Content:
{content[:2000]}

Founder Context & Story Bank:
{knowledge[:1200]}

Format clearly with headings."""

    ai_analysis = llm.generate_text(prompt, temperature=0.3)

    return {
        "status": "success",
        "title": title,
        "backend": res.get("backend"),
        "raw_summary": res.get("summary"),
        "ai_analysis": ai_analysis
    }

@router.post("/like")
def like_post(req: LikeRequest):
    """Likes a post on LinkedIn via headless browser."""
    return browser_agent.like_post(req.post_urn)

@router.post("/analyze-vision")
def analyze_vision(req: VisionAnalyzeRequest):
    """Analyzes a feed screenshot or custom image with multimodal vision AI."""
    image_path = None
    if req.image_url:
        if os.path.isabs(req.image_url) and os.path.exists(req.image_url):
            image_path = req.image_url
        else:
            # Convert relative url to filesystem path
            clean_url = str(req.image_url).replace("\\", "/").split("?")[0]
            filename = clean_url.split("/")[-1]
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            candidate = os.path.join(base_dir, "storage", "images", filename)
            if os.path.exists(candidate):
                image_path = candidate

    if not image_path or not os.path.exists(image_path):
        # Default to latest feed screenshot
        images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "images")
        if os.path.exists(images_dir):
            files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.startswith("feed_scan_")]
            if files:
                files.sort(key=os.path.getmtime, reverse=True)
                image_path = files[0]

    if not image_path or not os.path.exists(image_path):
        return {"status": "error", "message": "No screenshot available for vision analysis. Scan the feed first."}

    return vision_analyzer.analyze_screenshot(image_path, context_prompt=req.prompt)
