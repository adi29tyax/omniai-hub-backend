from sqlalchemy.orm import Session
import shutil
import os
from . import models, schemas, ffmpeg_worker
from app.storage.r2 import upload_public
from app.utils.logger import logger

async def compile_episode(db: Session, request: schemas.TimelineRequest) -> schemas.TimelineResponse:
    logger.info(f"Compiling episode '{request.episode_title}' for project {request.project_id}")
    # 1. Gather all assets for the requested scenes
    scene_assets = []
    
    for scene_id in request.scene_order:
        # Get animation clips
        animations = db.query(models.DirectorAsset).filter(
            models.DirectorAsset.scene_id == scene_id,
            models.DirectorAsset.type == "animation"
        ).all()
        
        # Get audio
        voices = db.query(models.DirectorAsset).filter(
            models.DirectorAsset.scene_id == scene_id,
            models.DirectorAsset.type == "voice"
        ).all()
        
        sfx = db.query(models.DirectorAsset).filter(
            models.DirectorAsset.scene_id == scene_id,
            models.DirectorAsset.type == "sfx"
        ).all()
        
        bgm = db.query(models.DirectorAsset).filter(
            models.DirectorAsset.scene_id == scene_id,
            models.DirectorAsset.type == "bgm"
        ).all()
        
        scene_assets.append({
            "scene_id": str(scene_id),
            "animations": [a.url for a in animations if a.url],
            "voices": [v.url for v in voices if v.url],
            "sfx": [s.url for s in sfx if s.url],
            "bgm": [b.url for b in bgm if b.url]
        })
        
    # 2. Call FFmpeg worker
    result = await ffmpeg_worker.compile_timeline(scene_assets, f"{request.episode_title}.mp4")
    
    if result.get("error"):
        raise Exception(f"FFmpeg Error: {result.get('error')} Logs: {result.get('log')}")
        
    output_path = result["output_path"]
    temp_dir = result["temp_dir"]
    
    # 3. Upload to R2
    try:
        with open(output_path, "rb") as f:
            video_bytes = f.read()
            
        upload_result = upload_public("episode_final.mp4", video_bytes)
        output_url = upload_result["url"]
        r2_key = upload_result.get("key")
        
    finally:
        # 4. Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    # 5. Save Episode Asset
    db_asset = models.DirectorAsset(
        project_id=request.project_id,
        type="episode",
        url=output_url,
        version=1,
        metadata_={
            "title": request.episode_title, 
            "scene_count": len(request.scene_order), 
            "r2_key": r2_key,
            "duration": result.get("duration"),
            "logs": result.get("log")
        },
        generation_settings={"engine": "ffmpeg"}
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return schemas.TimelineResponse(
        asset_id=db_asset.id,
        url=db_asset.url,
        metadata=db_asset.metadata_
    )
