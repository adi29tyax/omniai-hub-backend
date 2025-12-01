from . import model_workers
from .system_prompt import MUSIC_PROMPT
from app.modules.ide.utils import call_gemini
import json

async def generate_bgm(mood: str, pacing: str, duration: float = 30.0):
    # 1. Generate music prompt
    prompt = MUSIC_PROMPT(mood, pacing)
    gemini_output = await call_gemini(prompt)
    
    cleaned_output = gemini_output.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned_output)
        description = data.get("description", f"{mood} music with {pacing} pacing")
    except:
        description = f"{mood} music with {pacing} pacing"

    # 2. Call music generation model
    url = await model_workers.call_music_gen(description, duration)
    
    return {
        "description": description,
        "url": url
    }
