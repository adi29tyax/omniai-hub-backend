import json
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.ide.utils import call_gemini
from . import models, schemas, model_workers, sound_designer, music_generator, lip_sync
from .system_prompt import AUDIO_PROMPT
from app.utils.logger import logger

async def generate_voice(db: Session, request: schemas.AudioRequest) -> schemas.AudioResponse:
    logger.info(f"Generating voice for shot {request.shot_id}")
    # 1. Fetch character info
    character_name = "Unknown"
    if request.character_id:
        char = db.query(models.DirectorCharacter).filter(models.DirectorCharacter.id == request.character_id).first()
        if char:
            character_name = char.name
    
    # 2. Build prompt
    prompt = AUDIO_PROMPT(character_name, request.text, request.emotion or "neutral")
    gemini_output = await call_gemini(prompt)
    
    # 3. Parse JSON
    cleaned_output = gemini_output.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned_output)
        emotion_profile = data.get("emotion_profile", {})
        tts_prompt = data.get("tts_prompt", request.text)
    except:
        emotion_profile = {}
        tts_prompt = request.text

    # 4. Call TTS
    # Use a placeholder voice_id or fetch from character model if we added it
    voice_id = "default_voice" 
    # PATCH 3: Upload to R2
    # Simulating audio bytes from generation (placeholder)
    audio_bytes = b"fake_audio_bytes"
    from app.storage.r2 import upload_stream_to_r2
    result = upload_stream_to_r2(f"audio_{request.shot_id}.wav", audio_bytes)
    url = result["url"]
    
    # 5. Generate Lip Sync
    sync_data = lip_sync.generate_lip_sync(request.text, url)
    
    # 6. Save Asset
    metadata = {
        "text": request.text,
        "emotion_profile": emotion_profile,
        "tts_prompt": tts_prompt,
        "lip_sync": sync_data
    }
    if result.get("key"):
        metadata["r2_key"] = result["key"]
    
    db_asset = models.DirectorAsset(
        project_id=request.project_id,
        scene_id=request.scene_id,
        shot_id=request.shot_id,
        type="voice",
        url=url,
        version=1,
        metadata_=metadata,
        generation_settings={"engine": "placeholder"}
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return schemas.AudioResponse(
        asset_id=db_asset.id,
        url=db_asset.url,
        metadata=metadata
    )

async def generate_sfx(db: Session, request: schemas.SfxRequest):
    logger.info(f"Generating SFX for shot {request.shot_id}")
    results = await sound_designer.generate_sfx_for_action(request.action_description)
    
    assets = []
    for res in results:
        db_asset = models.DirectorAsset(
            project_id=request.project_id,
            scene_id=request.scene_id,
            shot_id=request.shot_id,
            type="sfx",
            url=res["url"],
            version=1,
            metadata_={"name": res["name"], "description": res["description"]},
            generation_settings={"engine": "placeholder"}
        )
        db.add(db_asset)
        assets.append(db_asset)
    
    db.commit()
    return assets

async def generate_bgm(db: Session, request: schemas.BgmRequest):
    logger.info(f"Generating BGM for scene {request.scene_id}")
    result = await music_generator.generate_bgm(request.mood, request.pacing)
    
    db_asset = models.DirectorAsset(
        project_id=request.project_id,
        scene_id=request.scene_id,
        type="bgm",
        url=result["url"],
        version=1,
        metadata_={"description": result["description"]},
        generation_settings={"engine": "placeholder"}
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return db_asset
