import os
import json
import httpx
from typing import AsyncGenerator, Dict, Any, List, Optional
from ..db import get_setting

# Known provider endpoints
PROVIDER_DEFAULTS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"]
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "o3-mini", "gpt-4.5-preview"]
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-sonnet-latest",
        "models": ["claude-3-7-sonnet-latest", "claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"]
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    },
    "kimi": {
        "base_url": "https://api.moonshot.ai/v1",
        "default_model": "moonshot-v1-auto",
        "models": ["moonshot-v1-auto", "moonshot-v1-8k", "moonshot-v1-32k"]
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "models": ["qwen-plus", "qwen-max", "qwen-turbo"]
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama3.2",
        "models": ["llama3.2", "qwen2.5:7b", "deepseek-r1:7b"]
    },
    "custom": {
        "base_url": "http://localhost:8000/v1",
        "default_model": "default-model",
        "models": ["default-model"]
    }
}

def get_active_llm_config() -> Dict[str, str]:
    """Retrieve current LLM configuration from database or env."""
    provider = get_setting("llm_provider", os.getenv("LLM_PROVIDER", "deepseek"))
    api_key = get_setting(f"{provider}_api_key", os.getenv(f"{provider.upper()}_API_KEY", ""))
    
    defaults = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["deepseek"])
    base_url = get_setting(f"{provider}_base_url", defaults["base_url"])
    model = get_setting(f"{provider}_model", defaults["default_model"])
    
    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": base_url,
        "model": model
    }

async def call_llm(messages: List[Dict[str, str]], temperature: float = 0.4, max_tokens: int = 4096) -> str:
    """Non-streaming LLM call."""
    config = get_active_llm_config()
    api_key = config["api_key"]
    base_url = config["base_url"].rstrip("/")
    model = config["model"]

    # Demo mode fallback if no API key is provided
    if not api_key and config["provider"] != "ollama":
        user_msg = messages[-1]["content"] if messages else ""
        return (
            "[离线演示模式 / Offline Demo Mode]\n\n"
            "尚未配置有效的 API Key。系统已提取最相关的资料分块：\n"
            f"根据您的输入与资料内容匹配分析完成。请在右上角「设置 / Settings」中填入 API Key 即可开启完整大模型智能回答与生成能力。"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    url = f"{base_url}/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

async def stream_llm(messages: List[Dict[str, str]], temperature: float = 0.4, max_tokens: int = 4096) -> AsyncGenerator[str, None]:
    """Streaming LLM call via Server-Sent Events (SSE)."""
    config = get_active_llm_config()
    api_key = config["api_key"]
    base_url = config["base_url"].rstrip("/")
    model = config["model"]

    # Demo mode fallback
    if not api_key and config["provider"] != "ollama":
        demo_text = (
            "【离线演示模式 / Offline Demo Mode】\n\n"
            "您尚未配置 API Key。系统正在以演示模式运行。\n"
            "请点击右上角「设置 / Settings」图标，配置 DeepSeek、OpenAI、Claude、Gemini、通义千问或本地 Ollama 的 API Key，即可体验全功能流式回答与精确行内引用！"
        )
        for char in demo_text:
            yield char
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

    url = f"{base_url}/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            if response.status_code != 200:
                error_body = await response.aread()
                yield f"Error from LLM Provider ({response.status_code}): {error_body.decode('utf-8', errors='ignore')}"
                return

            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue
