from typing import List, Dict
from openai import AsyncOpenAI
import json
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_scene_breakdown(story_text: str) -> List[Dict]:
    prompt = f"""
    Break this story into clean structured scenes.

    For each scene, return JSON with:
    - scene_id
    - title
    - summary
    - characters (list)
    - location
    - mood
    - time_of_day

    Story:
    {story_text}

    Return ONLY valid JSON.
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    try:
        parsed = json.loads(content)
        if "scenes" in parsed:
            return parsed["scenes"]
        return parsed
    except json.JSONDecodeError:
        return []
