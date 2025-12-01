from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from . import schemas, audio_service

router = APIRouter(tags=["Audio"])

@router.post("/generate-audio", response_model=schemas.AudioResponse)
async def generate_audio(request: schemas.AudioRequest, db: Session = Depends(get_db)):
    try:
        return await audio_service.generate_voice(db=db, request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-sfx", response_model=List[schemas.AssetResponse])
async def generate_sfx(request: schemas.SfxRequest, db: Session = Depends(get_db)):
    try:
        assets = await audio_service.generate_sfx(db=db, request=request)
        # Convert to AssetResponse schema
        return [
            schemas.AssetResponse(
                id=a.id,
                project_id=a.project_id,
                scene_id=a.scene_id,
                shot_id=a.shot_id,
                type=a.type,
                url=a.url,
                version=a.version,
                metadata=a.metadata_,
                generation_settings=a.generation_settings,
                created_at=a.created_at,
                updated_at=a.updated_at
            ) for a in assets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-bgm", response_model=schemas.AssetResponse)
async def generate_bgm(request: schemas.BgmRequest, db: Session = Depends(get_db)):
    try:
        a = await audio_service.generate_bgm(db=db, request=request)
        return schemas.AssetResponse(
            id=a.id,
            project_id=a.project_id,
            scene_id=a.scene_id,
            type=a.type,
            url=a.url,
            version=a.version,
            metadata=a.metadata_,
            generation_settings=a.generation_settings,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
