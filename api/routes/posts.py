from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.db.database import get_connection
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.skills.post_writer import PostWriter
from core.rules.humanizer import Humanizer
from core.linkedin.dispatcher import LinkedInDispatcher

router = APIRouter(prefix="/api/posts", tags=["posts"])

brain = BrainManager()
llm = OpenRouterClient()
post_writer = PostWriter(llm, brain)
dispatcher = LinkedInDispatcher()

class GeneratePostRequest(BaseModel):
    topic: str
    hook_code: str = "F7"
    founder_angle_code: Optional[str] = None
    target_length: str = "medium"
    visual_type: str = "ai_image"

class SavePostRequest(BaseModel):
    post_id: Optional[int] = None
    topic: str
    hook_formula: str
    content: str
    image_url: Optional[str] = None
    image_type: Optional[str] = None
    status: str = "draft"
    scheduled_time: Optional[str] = None
    flesch_score: Optional[float] = 70.0
    ai_tell_count: Optional[int] = 0

class HumanizeRequest(BaseModel):
    text: str

@router.get("")
def list_posts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/generate")
def generate_post(req: GeneratePostRequest):
    try:
        draft = post_writer.draft_post(
            topic=req.topic,
            hook_code=req.hook_code,
            founder_angle_code=req.founder_angle_code,
            target_length=req.target_length,
            visual_type=req.visual_type
        )
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
def save_post(req: SavePostRequest):
    conn = get_connection()
    cursor = conn.cursor()

    scheduled = req.scheduled_time
    if scheduled:
        scheduled = scheduled.replace("T", " ")
        if len(scheduled) == 16:
            scheduled += ":00"

    if req.post_id:
        cursor.execute('''
            UPDATE posts
            SET topic = ?, hook_formula = ?, content = ?, image_url = ?, image_type = ?,
                status = ?, scheduled_time = ?, flesch_score = ?, ai_tell_count = ?
            WHERE id = ?
        ''', (req.topic, req.hook_formula, req.content, req.image_url, req.image_type, req.status, scheduled, req.flesch_score, req.ai_tell_count, req.post_id))
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO posts (id, topic, hook_formula, content, image_url, image_type, status, scheduled_time, flesch_score, ai_tell_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (req.post_id, req.topic, req.hook_formula, req.content, req.image_url, req.image_type, req.status, scheduled, req.flesch_score, req.ai_tell_count))
        conn.commit()
        post_id = req.post_id
    else:
        cursor.execute('''
            INSERT INTO posts (topic, hook_formula, content, image_url, image_type, status, scheduled_time, flesch_score, ai_tell_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (req.topic, req.hook_formula, req.content, req.image_url, req.image_type, req.status, scheduled, req.flesch_score, req.ai_tell_count))
        conn.commit()
        post_id = cursor.lastrowid
    conn.close()
    return {"status": "saved", "post_id": post_id}

@router.get("/{post_id}")
def get_post(post_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return dict(row)

@router.delete("/{post_id}")
def delete_post(post_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, image_url FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")

    img_url = row["image_url"]
    if img_url and img_url.startswith("/storage/images/"):
        import os
        img_name = img_url.split("/")[-1]
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        img_path = os.path.join(base_dir, "storage", "images", img_name)
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception:
                pass

    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "post_id": post_id}

@router.post("/publish/{post_id}")
def publish_post(post_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if not post:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")

    res = dispatcher.publish_post(post["content"], post["image_url"])
    if res.get("status") != "error":
        cursor.execute('''
            UPDATE posts
            SET status = 'published', published_time = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (post_id,))
        conn.commit()
    conn.close()
    return {"status": res.get("status", "success"), "dispatch_result": res}

@router.post("/humanize")
def humanize_text_api(req: HumanizeRequest):
    cleaned, audit = Humanizer.humanize_text(req.text)
    return {
        "original_text": req.text,
        "humanized_text": cleaned,
        "audit": audit
    }

class RepurposeRequest(BaseModel):
    source_text: str
    source_type: str = "tweet"

class ExtractHookRequest(BaseModel):
    post_text: str

@router.post("/repurpose")
def repurpose_api(req: RepurposeRequest):
    from core.skills.repurposer import Repurposer
    repurposer = Repurposer(llm)
    return repurposer.repurpose_to_linkedin(source_text=req.source_text, source_type=req.source_type)

@router.post("/extract-hook")
def extract_hook_api(req: ExtractHookRequest):
    from core.skills.repurposer import HookExtractor
    extractor = HookExtractor(llm)
    return extractor.extract_hook(post_text=req.post_text)
