from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.skills.content_planner import ContentPlanner

router = APIRouter(prefix="/api/planner", tags=["planner"])

brain = BrainManager()
llm = OpenRouterClient()
planner = ContentPlanner(llm, brain)

class PlanRequest(BaseModel):
    focus_topic: Optional[str] = "AI Agents & High-Concurrency Systems"

@router.post("/generate")
def generate_weekly_plan(req: PlanRequest):
    try:
        plan_result = planner.create_weekly_plan(focus_topic=req.focus_topic or "AI Agents & High-Concurrency Systems")
        return plan_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
