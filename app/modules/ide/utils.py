import httpx
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)

# ------------------------------
# 1. CHATGPT CALL (Placeholder if no key)
# ------------------------------
async def call_chatgpt(prompt: str):
    if not OPENAI_API_KEY:
        return f"[ChatGPT Placeholder Mode] {prompt}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body, headers=headers)
        data = response.json()
        return data["choices"][0]["message"]["content"]


# ------------------------------
# 2. GEMINI CALL (Placeholder if no key)
# ------------------------------
async def call_gemini(prompt: str):
    if not GEMINI_API_KEY:
        return f"[Gemini Placeholder Mode] {prompt}"

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        data = response.json()
        
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return f"[Gemini Error] {str(data)}"
