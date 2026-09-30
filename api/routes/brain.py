from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from core.brain.brain import BrainManager
from core.brain.reflector import Reflector
from core.llm.client import OpenRouterClient

router = APIRouter(prefix="/api/brain", tags=["brain"])

brain = BrainManager()
llm = OpenRouterClient()
reflector = Reflector(llm)

class StoryItemRequest(BaseModel):
    category: str
    title: str
    detail: str
    metrics: Optional[str] = ""
    url: Optional[str] = ""
    year_or_date: Optional[str] = ""
    tags: Optional[str] = ""

class VoiceProfileRequest(BaseModel):
    tone: str
    cadence: str
    preferred_phrases: str
    banned_phrases: str
    cta_style: str
    author_bio: str

@router.get("/story-bank")
def get_story_bank():
    return brain.get_story_bank()

@router.post("/story-bank")
def add_story_bank_item(req: StoryItemRequest):
    story_id = brain.add_story(
        category=req.category,
        title=req.title,
        detail=req.detail,
        metrics=req.metrics or "",
        url=req.url or "",
        year_or_date=req.year_or_date or "",
        tags=req.tags or ""
    )
    return {"status": "created", "story_id": story_id}

@router.put("/story-bank/{story_id}")
def update_story_bank_item(story_id: int, req: StoryItemRequest):
    updated = brain.update_story(
        story_id=story_id,
        category=req.category,
        title=req.title,
        detail=req.detail,
        metrics=req.metrics or "",
        url=req.url or "",
        year_or_date=req.year_or_date or "",
        tags=req.tags or ""
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Story receipt not found")
    return {"status": "updated", "story_id": story_id}

@router.delete("/story-bank/{story_id}")
def delete_story_bank_item(story_id: int):
    deleted = brain.delete_story(story_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Story receipt not found")
    return {"status": "deleted"}

@router.get("/voice-profile")
def get_voice_profile():
    return brain.get_voice_profile()

@router.post("/voice-profile")
def update_voice_profile(req: VoiceProfileRequest):
    brain.update_voice_profile(
        tone=req.tone,
        cadence=req.cadence,
        preferred=req.preferred_phrases,
        banned=req.banned_phrases,
        cta_style=req.cta_style,
        bio=req.author_bio
    )
    return {"status": "updated"}

@router.get("/heuristics")
def get_heuristics():
    return brain.get_heuristics()

@router.post("/reflect")
def trigger_reflection():
    res = reflector.run_reflection_cycle()
    return res

@router.get("/reflections")
def get_reflections():
    return reflector.get_reflection_history()
