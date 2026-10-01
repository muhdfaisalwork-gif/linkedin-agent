import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from core.linkedin.browser_agent import LinkedInBrowserAgent
from core.llm.client import UniversalLLMClient
from core.llm.providers.ollama import OllamaProvider

router = APIRouter(prefix="/api/settings", tags=["settings"])
browser_agent = LinkedInBrowserAgent()
llm = UniversalLLMClient()

class SettingsUpdateRequest(BaseModel):
    llm_provider: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    anthropic_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    custom_base_url: Optional[str] = None
    custom_api_key: Optional[str] = None
    custom_model: Optional[str] = None
    execution_mode: Optional[str] = None
    publora_api_key: Optional[str] = None
    linkedin_platform_id: Optional[str] = None
    vision_model: Optional[str] = None

class CookieConnectRequest(BaseModel):
    cookie: str

@router.get("")
def get_settings():
    from core.db.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    db_settings = dict(cursor.fetchall())
    conn.close()

    provider = os.getenv("LLM_PROVIDER") or db_settings.get("LLM_PROVIDER", "openrouter")
    openrouter_model = os.getenv("OPENROUTER_MODEL") or db_settings.get("OPENROUTER_MODEL", "inclusionai/ling-3.0-flash-sante:free")
    openai_model = os.getenv("OPENAI_MODEL") or db_settings.get("OPENAI_MODEL", "gpt-4o")
    anthropic_model = os.getenv("ANTHROPIC_MODEL") or db_settings.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    gemini_model = os.getenv("GEMINI_MODEL") or db_settings.get("GEMINI_MODEL", "gemini-2.0-flash")
    ollama_model = os.getenv("OLLAMA_MODEL") or db_settings.get("OLLAMA_MODEL", "deepseek-r1:8b")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL") or db_settings.get("OLLAMA_BASE_URL", "http://localhost:11434")
    custom_base_url = os.getenv("CUSTOM_BASE_URL") or db_settings.get("CUSTOM_BASE_URL", "http://localhost:1234/v1")
    custom_model = os.getenv("CUSTOM_MODEL") or db_settings.get("CUSTOM_MODEL", "local-model")
    exec_mode = os.getenv("LINKEDIN_EXECUTION_MODE") or db_settings.get("LINKEDIN_EXECUTION_MODE", "manual")
    vision_model = os.getenv("VISION_MODEL") or db_settings.get("VISION_MODEL", "qwen2.5-vl")

    auth_file = os.path.join(browser_agent.user_data_dir, ".authenticated")
    auth_method = "unknown"
    if os.path.exists(auth_file):
        try:
            with open(auth_file, "r") as f:
                content = f.read()
                if "method=cookie" in content:
                    auth_method = "li_at_cookie"
                else:
                    auth_method = "browser_login"
        except Exception:
            pass

    # Probe local Ollama status
    ollama_provider = OllamaProvider(base_url=ollama_base_url)
    ollama_connected = ollama_provider.is_connected()
    ollama_installed_models = ollama_provider.list_models() if ollama_connected else []

    return {
        "llm_provider": provider,
        "openrouter_api_key_set": bool(os.getenv("OPENROUTER_API_KEY") or db_settings.get("OPENROUTER_API_KEY")),
        "openrouter_model": openrouter_model,
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY") or db_settings.get("OPENAI_API_KEY")),
        "openai_model": openai_model,
        "anthropic_api_key_set": bool(os.getenv("ANTHROPIC_API_KEY") or db_settings.get("ANTHROPIC_API_KEY")),
        "anthropic_model": anthropic_model,
        "gemini_api_key_set": bool(os.getenv("GEMINI_API_KEY") or db_settings.get("GEMINI_API_KEY")),
        "gemini_model": gemini_model,
        "ollama_base_url": ollama_base_url,
        "ollama_model": ollama_model,
        "ollama_connected": ollama_connected,
        "ollama_models": ollama_installed_models,
        "custom_base_url": custom_base_url,
        "custom_api_key_set": bool(os.getenv("CUSTOM_API_KEY") or db_settings.get("CUSTOM_API_KEY")),
        "custom_model": custom_model,
        "vision_model": vision_model,
        "available_free_models": llm.get_available_free_models(),
        "execution_mode": exec_mode,
        "browser_authenticated": browser_agent.is_authenticated(),
        "auth_method": auth_method,
        "playwright_available": browser_agent.is_playwright_available(),
        "publora_configured": bool((os.getenv("PUBLORA_API_KEY") or db_settings.get("PUBLORA_API_KEY")) and (os.getenv("LINKEDIN_PLATFORM_ID") or db_settings.get("LINKEDIN_PLATFORM_ID")))
    }

@router.get("/ollama-models")
def get_ollama_models(base_url: Optional[str] = None):
    """Probes local Ollama instance live and returns installed models."""
    prov = OllamaProvider(base_url=base_url)
    connected = prov.is_connected()
    models = prov.list_models() if connected else []
    return {
        "connected": connected,
        "base_url": prov.base_url,
        "models": models,
        "count": len(models)
    }

@router.post("")
def update_settings(req: SettingsUpdateRequest):
    from core.db.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    updates = {}
    if req.llm_provider:
        os.environ["LLM_PROVIDER"] = req.llm_provider
        updates["LLM_PROVIDER"] = req.llm_provider

    if req.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = req.openrouter_api_key
        updates["OPENROUTER_API_KEY"] = req.openrouter_api_key
    if req.openrouter_model:
        os.environ["OPENROUTER_MODEL"] = req.openrouter_model
        updates["OPENROUTER_MODEL"] = req.openrouter_model

    if req.openai_api_key:
        os.environ["OPENAI_API_KEY"] = req.openai_api_key
        updates["OPENAI_API_KEY"] = req.openai_api_key
    if req.openai_model:
        os.environ["OPENAI_MODEL"] = req.openai_model
        updates["OPENAI_MODEL"] = req.openai_model

    if req.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = req.anthropic_api_key
        updates["ANTHROPIC_API_KEY"] = req.anthropic_api_key
    if req.anthropic_model:
        os.environ["ANTHROPIC_MODEL"] = req.anthropic_model
        updates["ANTHROPIC_MODEL"] = req.anthropic_model

    if req.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = req.gemini_api_key
        updates["GEMINI_API_KEY"] = req.gemini_api_key
    if req.gemini_model:
        os.environ["GEMINI_MODEL"] = req.gemini_model
        updates["GEMINI_MODEL"] = req.gemini_model

    if req.ollama_base_url:
        os.environ["OLLAMA_BASE_URL"] = req.ollama_base_url
        updates["OLLAMA_BASE_URL"] = req.ollama_base_url
    if req.ollama_model:
        os.environ["OLLAMA_MODEL"] = req.ollama_model
        updates["OLLAMA_MODEL"] = req.ollama_model

    if req.custom_base_url:
        os.environ["CUSTOM_BASE_URL"] = req.custom_base_url
        updates["CUSTOM_BASE_URL"] = req.custom_base_url
    if req.custom_api_key:
        os.environ["CUSTOM_API_KEY"] = req.custom_api_key
        updates["CUSTOM_API_KEY"] = req.custom_api_key
    if req.custom_model:
        os.environ["CUSTOM_MODEL"] = req.custom_model
        updates["CUSTOM_MODEL"] = req.custom_model

    if req.execution_mode:
        os.environ["LINKEDIN_EXECUTION_MODE"] = req.execution_mode
        updates["LINKEDIN_EXECUTION_MODE"] = req.execution_mode
    if req.publora_api_key:
        os.environ["PUBLORA_API_KEY"] = req.publora_api_key
        updates["PUBLORA_API_KEY"] = req.publora_api_key
    if req.linkedin_platform_id:
        os.environ["LINKEDIN_PLATFORM_ID"] = req.linkedin_platform_id
        updates["LINKEDIN_PLATFORM_ID"] = req.linkedin_platform_id
    if req.vision_model:
        os.environ["VISION_MODEL"] = req.vision_model
        updates["VISION_MODEL"] = req.vision_model

    for k, v in updates.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

    return {"status": "saved", "message": "Settings updated and persisted to database."}

@router.post("/save-cookie")
def save_linkedin_cookie(req: CookieConnectRequest):
    """Saves and verifies direct li_at session cookie in <2 seconds."""
    res = browser_agent.save_cookie(req.cookie)
    return res

@router.post("/disconnect")
def disconnect_session():
    """Disconnects and clears current LinkedIn session."""
    res = browser_agent.disconnect()
    return res

@router.post("/connect-browser")
def connect_browser_session():
    res = browser_agent.launch_interactive_login()
    return res
