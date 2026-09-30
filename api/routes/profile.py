from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.db.database import get_connection
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.skills.profile_optimizer import ProfileOptimizer
from core.linkedin.dispatcher import LinkedInDispatcher

router = APIRouter(prefix="/api/profile", tags=["profile"])

brain = BrainManager()
llm = OpenRouterClient()
profile_optimizer = ProfileOptimizer(llm, brain)
dispatcher = LinkedInDispatcher()

class OptimizeProfileRequest(BaseModel):
    notes_or_profile: str
    goal: str = "clients_and_authority"

class ApplyProfileRequest(BaseModel):
    headline: Optional[str] = None
    about: Optional[str] = None

@router.get("/current")
def get_current_optimizations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profile_optimizations ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/optimize")
def optimize_profile(req: OptimizeProfileRequest):
    try:
        result = profile_optimizer.optimize_profile(
            user_notes_or_profile=req.notes_or_profile,
            goal=req.goal
        )
        # Save record
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profile_optimizations (section, current_content, optimized_content)
            VALUES (?, ?, ?)
        ''', ("Full Profile", req.notes_or_profile, result["optimized_content"]))
        conn.commit()
        conn.close()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply")
def apply_profile_changes(req: ApplyProfileRequest):
    try:
        res = dispatcher.update_profile(headline=req.headline, about=req.about)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
