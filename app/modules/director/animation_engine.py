from openai import AsyncOpenAI
from typing import List, Dict, Any
import json

client = AsyncOpenAI()
OWNER_EMAIL = "csadityasharma2000@gmail.com"

async def generate_animation_blocks(payload: Dict[str, Any], user: Any) -> List[Dict[str, Any]]:
    # Validate owner mode (bypass limits)
    is_owner = hasattr(user, "email") and user.email == OWNER_EMAIL
    
    # Note: Usage limits are typically enforced by middleware/router dependencies.
    # Here we ensure the engine is aware of the owner context if needed for priority or advanced models.
    
    keyframes = payload.get("keyframes", [])
    shot_metadata = payload.get("shot_metadata", {})
    
    prompt = f"""
    You are a professional cinematic animation director.
    
    Generate animation blocks connecting the following keyframes:
    {json.dumps(keyframes, indent=2)}
    
    Shot Metadata:
    {json.dumps(shot_metadata, indent=2)}
    
    For each transition between keyframes (or for the whole shot), provide:
    - from_keyframe (id)
    - to_keyframe (id)
    - duration (in seconds, float)
    - motion (cinematic description of subject motion)
    - camera_movement (cinematic description of camera move)
    - easing (e.g., linear, ease-in-out, cinematic-slow)
    - metadata (any technical details)

    Return a JSON object with a key "animation_blocks" containing the list of blocks.
    """

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    # Assuming the environment returns parsed JSON in message["parsed"] as per previous module
    try:
        return response.choices[0].message["parsed"]["animation_blocks"]
    except (KeyError, TypeError):
        # Fallback if "parsed" is not available or structure differs
        content = response.choices[0].message.content
        if content:
            data = json.loads(content)
            return data.get("animation_blocks", [])
        return []
