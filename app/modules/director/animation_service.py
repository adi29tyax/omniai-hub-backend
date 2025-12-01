import json
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.ide.utils import call_gemini
from . import models, schemas, model_workers
from .system_prompt import ANIMATION_PROMPT
from app.utils.logger import logger

# Placeholder for Llama call
async def call_llama(prompt: str):
    # Simulating Llama call with Gemini
    return await call_gemini(prompt)

async def generate_animation(db: Session, request: schemas.AnimationRequest) -> schemas.AnimationResponse:
    logger.info(f"Generating animation for shot {request.shot_id} with model {request.model}")
    # 1. Load shot info from DB
    shot = db.query(models.DirectorShot).filter(models.DirectorShot.id == request.shot_id).first()
    if not shot:
        raise ValueError("Shot not found")
    
    # 2. Load keyframe metadata
    # We assume there's a keyframe asset associated with this shot.
    # We pick the latest version or a specific one if we had that info.
    # For now, let's find the most recent keyframe asset for this shot.
    keyframe_asset = db.query(models.DirectorAsset).filter(
        models.DirectorAsset.shot_id == request.shot_id,
        models.DirectorAsset.type == "keyframe"
    ).order_by(models.DirectorAsset.created_at.desc()).first()
    
    keyframe_prompt = ""
    style = "Anime" # Default style if not found
    
    if keyframe_asset and keyframe_asset.metadata_:
        # metadata_ stores the JSON from keyframe generation
        keyframe_data = keyframe_asset.metadata_
        if isinstance(keyframe_data, str):
             try:
                 keyframe_data = json.loads(keyframe_data)
             except:
                 pass
        
        if isinstance(keyframe_data, dict):
            keyframe_prompt = keyframe_data.get("positive", "")
            style = keyframe_data.get("style", "Anime")
    
    # Override prompt if provided
    if request.override_prompt:
        keyframe_prompt = request.override_prompt

    # 3. Build animation prompt
    # We wrap shot data to match what the prompt expects
    class ShotWrapper:
        def __init__(self, s):
            self.camera = s.camera
            self.action = s.action

    shot_wrapper = ShotWrapper(shot)
    prompt = ANIMATION_PROMPT(shot_wrapper, keyframe_prompt, style)
    
    # 4. Call Gemini
    gemini_output = await call_gemini(prompt)
    
    # 5. Call Llama (Fix JSON + optimize for video generation)
    fix_prompt = f"Fix this JSON to match the schema {{'positive': '...', ...}} and optimize the 'positive' prompt for video generation model {request.model}: {gemini_output}"
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

    video_prompt = parsed_data["positive"]

    # 6. Call model based on request
    # PATCH 3: Upload to R2
    # Simulating video bytes from generation (placeholder)
    video_bytes = b"fake_video_bytes"
    from app.storage.r2 import upload_stream_to_r2
    result = upload_stream_to_r2(f"animation_{request.shot_id}.mp4", video_bytes)
    video_url = result["url"]

    # 7. Save animation clip as Asset
    asset_metadata = parsed_data
    if result.get("key"):
        asset_metadata["r2_key"] = result["key"]
    
    db_asset = models.DirectorAsset(
        project_id=request.project_id,
        scene_id=request.scene_id,
        shot_id=request.shot_id,
        type="animation",
        url=video_url,
        version=1,
        metadata_=asset_metadata,
        generation_settings={
            "model": request.model,
            "duration": request.duration,
            "style": style
        }
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    # 8. Return AnimationResponse
    return schemas.AnimationResponse(
        asset_id=db_asset.id,
        url=db_asset.url,
        version=db_asset.version,
        metadata=asset_metadata,
        generation_settings=db_asset.generation_settings
    )
