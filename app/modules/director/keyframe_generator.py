from openai import AsyncOpenAI
client = AsyncOpenAI()

async def generate_keyframes(shot):
    prompt = f"""
    You are a professional cinematic storyboard keyframe artist.

    Generate keyframes for the following shot:
    {shot}

    For each keyframe, use:
    - id
    - prompt (visual description)
    - camera (angle + motion)
    - lighting
    - mood
    - details

    Keep responses short, cinematic, and JSON structured.
    """

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    return response.choices[0].message["parsed"]["keyframes"]
