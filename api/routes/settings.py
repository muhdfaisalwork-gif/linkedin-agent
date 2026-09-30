import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from core.linkedin.browser_agent import LinkedInBrowserAgent
from core.llm.client import OpenRouterClient

router = APIRouter(prefix="/api/settings", tags=["settings"])
browser_agent = LinkedInBrowserAgent()
llm = OpenRouterClient()

class SettingsUpdateRequest(BaseModel):
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    execution_mode: Optional[str] = None
    publora_api_key: Optional[str] = None
    linkedin_platform_id: Optional[str] = None

@router.get("")
def get_settings():
    from core.db.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    db_settings = dict(cursor.fetchall())
    conn.close()

    model = os.getenv("OPENROUTER_MODEL") or db_settings.get("OPENROUTER_MODEL", "openrouter/free")
    exec_mode = os.getenv("LINKEDIN_EXECUTION_MODE") or db_settings.get("LINKEDIN_EXECUTION_MODE", "manual")

    return {
        "openrouter_api_key_set": bool(os.getenv("OPENROUTER_API_KEY") or db_settings.get("OPENROUTER_API_KEY")),
        "openrouter_model": model,
        "available_free_models": llm.get_available_free_models(),
        "execution_mode": exec_mode,
        "browser_authenticated": browser_agent.is_authenticated(),
        "playwright_available": browser_agent.is_playwright_available(),
        "publora_configured": bool((os.getenv("PUBLORA_API_KEY") or db_settings.get("PUBLORA_API_KEY")) and (os.getenv("LINKEDIN_PLATFORM_ID") or db_settings.get("LINKEDIN_PLATFORM_ID")))
    }

@router.post("")
def update_settings(req: SettingsUpdateRequest):
    from core.db.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    updates = {}
    if req.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = req.openrouter_api_key
        updates["OPENROUTER_API_KEY"] = req.openrouter_api_key
    if req.openrouter_model:
        os.environ["OPENROUTER_MODEL"] = req.openrouter_model
        updates["OPENROUTER_MODEL"] = req.openrouter_model
    if req.execution_mode:
        os.environ["LINKEDIN_EXECUTION_MODE"] = req.execution_mode
        updates["LINKEDIN_EXECUTION_MODE"] = req.execution_mode
    if req.publora_api_key:
        os.environ["PUBLORA_API_KEY"] = req.publora_api_key
        updates["PUBLORA_API_KEY"] = req.publora_api_key
    if req.linkedin_platform_id:
        os.environ["LINKEDIN_PLATFORM_ID"] = req.linkedin_platform_id
        updates["LINKEDIN_PLATFORM_ID"] = req.linkedin_platform_id

    for k, v in updates.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

    return {"status": "saved", "message": "Settings updated and persisted to database."}

@router.post("/connect-browser")
def connect_browser_session():
    res = browser_agent.launch_interactive_login()
    return res
