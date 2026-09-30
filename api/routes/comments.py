from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.db.database import get_connection
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.skills.reply_handler import ReplyHandler

router = APIRouter(prefix="/api/comments", tags=["comments"])

brain = BrainManager()
llm = OpenRouterClient()
reply_handler = ReplyHandler(llm, brain)

class SweepRequest(BaseModel):
    post_context: str
    sample_comments: List[Dict[str, Any]]

class ReplyRequest(BaseModel):
    post_context: str
    comment_text: str
    commenter_name: str
    depth: int = 1
    top_level_urn: Optional[str] = None

@router.get("")
def list_comments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/draft-reply")
def draft_reply_endpoint(req: ReplyRequest):
    try:
        reply_data = reply_handler.draft_reply(
            original_post=req.post_context,
            comment_text=req.comment_text,
            commenter_name=req.commenter_name,
            depth=req.depth,
            top_level_urn=req.top_level_urn
        )
        return reply_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sweep")
def sweep_comments(req: SweepRequest):
    try:
        actionable, filtered = reply_handler.filter_comments(req.sample_comments)
        drafts = []
        for c in actionable:
            draft = reply_handler.draft_reply(
                original_post=req.post_context,
                comment_text=c.get("text", ""),
                commenter_name=c.get("author", "Commenter"),
                depth=c.get("depth", 1),
                top_level_urn=c.get("top_level_urn")
            )
            drafts.append(draft)

        return {
            "total_comments": len(req.sample_comments),
            "actionable_count": len(actionable),
            "filtered_count": len(filtered),
            "filtered_out": filtered,
            "drafts": drafts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExternalCommentRequest(BaseModel):
    post_text: str
    author_name: str = "Author"

@router.post("/draft-external")
def draft_external_comment(req: ExternalCommentRequest):
    try:
        from core.skills.comment_drafter import CommentDrafter
        drafter = CommentDrafter(llm, brain)
        return drafter.draft_comment(post_text=req.post_text, author_name=req.author_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SendReplyRequest(BaseModel):
    post_url: str
    reply_text: str

@router.post("/send-reply")
def send_comment_reply(req: SendReplyRequest):
    try:
        from core.linkedin.dispatcher import LinkedInDispatcher
        dispatcher = LinkedInDispatcher()
        return dispatcher.reply_to_comment(post_url=req.post_url, reply_text=req.reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
