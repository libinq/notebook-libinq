import json
import re
from typing import Dict, Any, Tuple
from ..llm.prompts import STUDIO_PROMPTS
from ..llm.provider import call_llm
from .pptx_exporter import create_pptx_from_outline

def extract_json_block(text: str) -> Any:
    """Safely extract and parse JSON object or array."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    # Find { ... } or [ ... ]
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        return json.loads(text)
    except Exception:
        return text

async def generate_studio_artifact(
    artifact_type: str,
    sources_context: str,
    language: str = "zh"
) -> Dict[str, Any]:
    """
    Generate a studio artifact (MindMap, Briefing, Study Guide, FAQ, Timeline, Quiz, Flashcards, Presentation).
    """
    prompt_template = STUDIO_PROMPTS.get(artifact_type)
    if not prompt_template:
        raise ValueError(f"Unknown artifact type: {artifact_type}")

    lang_str = "Simplified Chinese (简体中文)" if language.startswith("zh") or "chinese" in language.lower() else "English"
    formatted_prompt = prompt_template.format(lang=lang_str, sources_context=sources_context)

    messages = [
        {"role": "system", "content": "You are a senior research analyst and knowledge visualization expert."},
        {"role": "user", "content": formatted_prompt}
    ]

    raw_response = await call_llm(messages, temperature=0.3, max_tokens=4096)

    # Process structure based on type
    if artifact_type in ["mindmap", "flashcards", "presentation"]:
        parsed_data = extract_json_block(raw_response)
        
        # If presentation, optionally generate PPTX
        pptx_url = ""
        if artifact_type == "presentation" and isinstance(parsed_data, dict):
            try:
                pptx_path = create_pptx_from_outline(parsed_data)
                pptx_url = f"/api/studio/download/{pptx_path.name}"
            except Exception:
                pass

        return {
            "type": artifact_type,
            "raw": raw_response,
            "data": parsed_data,
            "pptx_url": pptx_url
        }
    else:
        # Markdown artifacts (briefing, study_guide, faq, timeline, quiz)
        return {
            "type": artifact_type,
            "raw": raw_response,
            "markdown": raw_response
        }
