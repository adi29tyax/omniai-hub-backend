import json
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.ide.utils import call_gemini
from . import models, schemas
from .system_prompt import KEYFRAME_PROMPT
from app.utils.logger import logger

# Placeholder for Llama call
async def call_llama(prompt: str):
    # Simulating Llama call with Gemini
    return await call_gemini(prompt)

async def generate_keyframe(db: Session, request: schemas.KeyframeRequest) -> schemas.KeyframeResponse:
    logger.info(f"Generating keyframe for shot {request.shot_id}")
    # 1. Load shot info from DB
    shot = db.query(models.DirectorShot).filter(models.DirectorShot.id == request.shot_id).first()
    if not shot:
        raise ValueError("Shot not found")
    
    # 2. Load related characters from story
    # We need to find the story_id first. 
    # Shot -> Scene -> Story
    scene = db.query(models.DirectorScene).filter(models.DirectorScene.id == request.scene_id).first()
    if not scene:
        raise ValueError("Scene not found")
        
    characters = db.query(models.DirectorCharacter).filter(models.DirectorCharacter.story_id == scene.story_id).all()
    character_data = [{"name": c.name, "description": c.description, "visual_style": c.visual_style} for c in characters]
    
    # 3. Build system prompt
    # If override_prompt is provided, we might use it directly or mix it. 
    # The prompt implies we use the shot details but maybe override the 'original prompt' part.
    # Let's pass the override prompt as the 'prompt' in the shot object wrapper if present.
    
    class ShotWrapper:
        def __init__(self, s, override=None):
            self.type = s.type
            self.camera = s.camera
            self.action = s.action
            self.prompt = override if override else s.prompt

    shot_wrapper = ShotWrapper(shot, request.override_prompt)
    
    prompt = KEYFRAME_PROMPT(shot_wrapper, request.style, character_data)
    
    # 4. Call Gemini
    gemini_output = await call_gemini(prompt)
    
    # 5. Call Llama (Fix JSON + optimize for Flux)
    fix_prompt = f"Fix this JSON to match the schema {{'positive': '...', ...}} and optimize the 'positive' prompt for Flux.1-dev: {gemini_output}"
    llama_output = await call_llama(fix_prompt)
    
    # Validate JSON
    cleaned_output = llama_output.replace("```json", "").replace("```", "").strip()
    try:
        parsed_data = json.loads(cleaned_output)
        if "positive" not in parsed_data:
             raise ValueError("Invalid JSON structure: missing 'positive' key")
    except json.JSONDecodeError:
        # Fallback to Gemini output
        try:
            cleaned_gemini = gemini_output.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(cleaned_gemini)
        except json.JSONDecodeError:
             raise ValueError("Failed to generate valid JSON from AI response")

    # 6. Call model (placeholder)
    # In a real system, we would send `parsed_data['positive']` to a Flux API.
    # Here we just generate a placeholder URL.
    # PATCH 3: Upload to R2
    # Simulating image bytes from generation (placeholder)
    image_bytes = b"fake_image_bytes" 
    from app.storage.r2 import upload_stream_to_r2
    result = upload_stream_to_r2(f"keyframe_{request.shot_id}.png", image_bytes)
    
    generated_image_url = result["url"]
    
    # 7. Create Asset entry
    asset_metadata = parsed_data # Store the full generation metadata
    if result.get("key"):
        asset_metadata["r2_key"] = result["key"]
    
    db_asset = models.DirectorAsset(
        project_id=request.project_id,
        scene_id=request.scene_id,
        shot_id=request.shot_id,
        type="keyframe",
        url=generated_image_url,
        version=1,
        metadata_=asset_metadata, # Mapping to metadata_ column
        generation_settings={
            "model": "Flux.1-dev",
            "steps": 30,
            "guidance": 7.5,
            "style": request.style
        }
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    # 8. Return KeyframeResponse
    return schemas.KeyframeResponse(
        asset_id=db_asset.id,
        url=db_asset.url,
        version=db_asset.version,
        metadata=asset_metadata,
        generation_settings=db_asset.generation_settings
    )
