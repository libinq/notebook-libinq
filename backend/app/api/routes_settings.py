import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..db import get_setting, set_setting
from ..llm.provider import PROVIDER_DEFAULTS, get_active_llm_config

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None

class ConnectionTestRequest(BaseModel):
    provider: str
    api_key: str
    base_url: str
    model: str

@router.get("")
def get_settings():
    active_provider = get_setting("llm_provider", "deepseek")
    
    # Build list of providers and their configured status
    providers_info = {}
    for prov, default_val in PROVIDER_DEFAULTS.items():
        saved_key = get_setting(f"{prov}_api_key", "")
        saved_url = get_setting(f"{prov}_base_url", default_val["base_url"])
        saved_model = get_setting(f"{prov}_model", default_val["default_model"])
        
        has_key = bool(saved_key) or prov == "ollama"
        masked_key = (saved_key[:3] + "..." + saved_key[-4:]) if len(saved_key) > 7 else ("***" if saved_key else "")
        
        providers_info[prov] = {
            "has_key": has_key,
            "masked_key": masked_key,
            "base_url": saved_url,
            "model": saved_model,
            "available_models": default_val["models"]
        }

    return {
        "active_provider": active_provider,
        "providers": providers_info
    }

@router.post("")
def save_settings(req: SettingsUpdate):
    provider = req.provider.lower()
    set_setting("llm_provider", provider)
    
    if req.api_key is not None and req.api_key.strip():
        set_setting(f"{provider}_api_key", req.api_key.strip())
    if req.base_url is not None and req.base_url.strip():
        set_setting(f"{provider}_base_url", req.base_url.strip())
    if req.model is not None and req.model.strip():
        set_setting(f"{provider}_model", req.model.strip())

    return {"status": "saved", "active_provider": provider}

@router.post("/test")
async def test_connection(req: ConnectionTestRequest):
    headers = {
        "Authorization": f"Bearer {req.api_key.strip()}",
        "Content-Type": "application/json"
    }
    url = f"{req.base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": req.model.strip(),
        "messages": [{"role": "user", "content": "Respond with 'OK'"}],
        "max_tokens": 5
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                return {"status": "success", "message": "Connection verified successfully! 连接测试成功！"}
            else:
                return {"status": "error", "message": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}
