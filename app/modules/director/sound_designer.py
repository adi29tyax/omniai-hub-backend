import json
from . import model_workers
from .system_prompt import SFX_PROMPT
from app.modules.ide.utils import call_gemini

async def generate_sfx_for_action(action: str):
    # 1. Analyze action to get list of SFX
    prompt = SFX_PROMPT(action)
    gemini_output = await call_gemini(prompt)
    
    # Simple parsing
    cleaned_output = gemini_output.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned_output)
        sfx_list = data.get("sfx_list", [])
    except:
        sfx_list = [{"name": "default_sfx", "description": action}]

    # 2. Generate audio for each SFX
    results = []
    for sfx in sfx_list:
        url = await model_workers.call_sfx_gen(sfx["description"])
        results.append({
            "name": sfx["name"],
            "description": sfx["description"],
            "url": url
        })
    
    return results
