from typing import List, Dict
from openai import AsyncOpenAI
import json
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_shot_breakdown(scene: Dict) -> List[Dict]:
    prompt = f"""
    Generate a list of cinematic SHOTS for this scene.
    Use professional filmmaking terminology.

    Scene data:
    {json.dumps(scene, indent=2)}

    For each shot return JSON with:
    - shot_id
    - description
    - camera_angle
    - camera_motion
    - lighting
    - focus
    - mood
    - keyframe_count (default 3)

    Keep JSON clean and structured.
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        parsed = json.loads(content)
        if "shots" in parsed:
            return parsed["shots"]
        return parsed
    except json.JSONDecodeError:
        return []
