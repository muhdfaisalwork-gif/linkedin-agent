from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.db.database import get_connection
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.skills.inbox_handler import InboxHandler

router = APIRouter(prefix="/api/inbox", tags=["inbox"])

brain = BrainManager()
llm = OpenRouterClient()
inbox_handler = InboxHandler(llm, brain)

class ProcessMessageRequest(BaseModel):
    sender_name: str
    sender_title: str
    message_text: str
    history: Optional[List[Dict[str, str]]] = None

@router.get("")
def list_inbox():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inbox_messages ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/process")
def process_incoming_message(req: ProcessMessageRequest):
    try:
        res = inbox_handler.process_message(
            sender_name=req.sender_name,
            sender_title=req.sender_title,
            message_text=req.message_text,
            conversation_history=req.history
        )

        # Store in inbox_messages table
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inbox_messages (sender_name, sender_title, message_text, intent_category, suggested_reply, status)
            VALUES (?, ?, ?, ?, ?, 'drafted')
        ''', (req.sender_name, req.sender_title, req.message_text, res["intent"], res["reply_draft"]))
        conn.commit()
        msg_id = cursor.lastrowid
        conn.close()

        res["id"] = msg_id
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class UpdateInboxStatusRequest(BaseModel):
    status: str

@router.patch("/{msg_id}")
def update_inbox_status(msg_id: int, req: UpdateInboxStatusRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE inbox_messages SET status = ? WHERE id = ?", (req.status, msg_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "updated", "id": msg_id, "new_status": req.status}

@router.delete("/{msg_id}")
def delete_inbox_message(msg_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inbox_messages WHERE id = ?", (msg_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "deleted", "id": msg_id}
