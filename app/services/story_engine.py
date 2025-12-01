import json
import httpx
from ..config import settings
from ..schemas.director import StoryRequest, StoryResponse


# -----------------------------
# SYSTEM PROMPT (FROM GEMINI)
# -----------------------------
SYSTEM_PROMPT = """
You are the AI Director for OmniAI Studio, a high-end anime production engine. 
Your goal is to take a user's raw concept and convert it into a structured, cinematic shot list in valid JSON format.

RULES:
1. OUTPUT FORMAT: Strictly JSON only. No markdown, no conversational text.
2. HIERARCHY: Story -> Scene -> Shots.
3. PACING: Each Shot represents 3-5 seconds of video.
4. VISUALS: visual_description must be highly descriptive, focusing on lighting, color, and composition.
5. CONSISTENCY: Maintain character names and specific visual traits across shots.
6. STYLE: Adapt keywords based on the user's selected Style Mode.

JSON STRUCTURE:
{
  "title": "String",
  "logline": "String",
  "characters": [
    {
      "name": "String",
      "visual_traits": "String"
    }
  ],
  "scenes": [
    {
      "scene_number": Integer,
      "location": "String",
      "shots": [
        {
          "shot_number": Integer,
          "camera_angle": "String",
          "subject": "String",
          "action": "String",
          "visual_prompt": "String",
          "dialogue": "String or null",
          "audio_mood": "String"
        }
      ]
    }
  ]
}
"""


# -----------------------------
# LLM CALLER (GROQ or TOGETHER)
# -----------------------------
async def call_story_engine(req: StoryRequest) -> StoryResponse:
    """Calls the LLM and returns validated StoryResponse"""

    user_prompt = f"""
Project Concept: {req.concept}
Genre: {req.genre}
Target Style: {req.style_mode}

Generate a pilot episode script consisting of 1 Scene with 4–6 Shots.
Make it cinematic and exciting.
"""

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            settings.LLM_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"}
        )

    text = r.json()["choices"][0]["message"]["content"]

    # Parse JSON safely
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    # Validate schema
    return StoryResponse(**data)
