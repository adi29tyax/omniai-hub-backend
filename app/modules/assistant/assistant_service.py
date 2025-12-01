import json
from app.modules.ide.utils import call_gemini
from . import schemas
from .system_prompt import ASSISTANT_PROMPT

async def process_query(request: schemas.AssistantRequest) -> schemas.AssistantResponse:
    # 1. Build Prompt
    prompt = ASSISTANT_PROMPT(request.mode, request.context)
    prompt += f"\nUSER QUERY: {request.message}"
    
    # 2. Call Gemini
    gemini_output = await call_gemini(prompt)
    
    # 3. Parse JSON
    cleaned_output = gemini_output.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned_output)
        response_text = data.get("response", "I couldn't process that request.")
        actions = data.get("actions", [])
        metadata_fixes = data.get("metadata_fixes")
        improved_prompt = data.get("improved_prompt")
    except:
        # Fallback if JSON fails
        response_text = gemini_output
        actions = []
        metadata_fixes = None
        improved_prompt = None

    return schemas.AssistantResponse(
        response=response_text,
        actions=[schemas.AssistantAction(**a) for a in actions],
        metadata_fixes=metadata_fixes,
        improved_prompt=improved_prompt
    )
