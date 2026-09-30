from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from core.db.database import get_connection
from core.brain.brain import BrainManager

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
brain = BrainManager()

class SimulateMetricsRequest(BaseModel):
    post_id: int
    impressions: int
    likes: int
    comments: int
    reposts: int
    saves: int

@router.get("/overview")
def get_analytics_overview():
    conn = get_connection()
    cursor = conn.cursor()

    # Total posts count by status
    cursor.execute("SELECT status, COUNT(*) as count FROM posts GROUP BY status")
    posts_by_status = {r["status"]: r["count"] for r in cursor.fetchall()}

    # Aggregate performance
    cursor.execute('''
        SELECT SUM(impressions) as total_impressions,
               SUM(likes) as total_likes,
               SUM(comments) as total_comments,
               SUM(reposts) as total_reposts,
               SUM(saves) as total_saves
        FROM post_analytics
    ''')
    totals_row = cursor.fetchone()
    totals = {
        "impressions": totals_row["total_impressions"] or 0,
        "likes": totals_row["total_likes"] or 0,
        "comments": totals_row["total_comments"] or 0,
        "reposts": totals_row["total_reposts"] or 0,
        "saves": totals_row["total_saves"] or 0,
    }

    # Top performing hook formulas
    cursor.execute('''
        SELECT formula_code, formula_name, weight, usage_count, avg_engagement_rate
        FROM heuristics
        ORDER BY weight DESC LIMIT 6
    ''')
    top_formulas = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "posts_by_status": posts_by_status,
        "totals": totals,
        "top_formulas": top_formulas
    }

@router.post("/simulate")
def simulate_post_metrics(req: SimulateMetricsRequest):
    brain.record_post_performance(
        post_id=req.post_id,
        impressions=req.impressions,
        likes=req.likes,
        comments=req.comments,
        reposts=req.reposts,
        saves=req.saves
    )
    return {"status": "recorded", "message": "Performance metrics recorded and heuristics evolved."}

class SegmentEngagersRequest(BaseModel):
    engagers: List[Dict[str, str]]

class AdvocacyPackRequest(BaseModel):
    company_update: str

@router.post("/segment-engagers")
def segment_engagers_api(req: SegmentEngagersRequest):
    from core.skills.analytics import EngagerAnalytics
    from core.llm.client import OpenRouterClient
    analytics = EngagerAnalytics(OpenRouterClient())
    return analytics.segment_engagers(req.engagers)

@router.post("/advocacy-pack")
def advocacy_pack_api(req: AdvocacyPackRequest):
    from core.skills.analytics import EmployeeAdvocacy
    from core.llm.client import OpenRouterClient
    advocacy = EmployeeAdvocacy(OpenRouterClient())
    return advocacy.create_advocacy_brief(req.company_update)
