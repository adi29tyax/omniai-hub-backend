from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from . import schemas, keyframe_service

router = APIRouter(tags=["Keyframe"])

@router.post("/generate-keyframe", response_model=schemas.KeyframeResponse)
async def generate_keyframe(request: schemas.KeyframeRequest, db: Session = Depends(get_db)):
    try:
        return await keyframe_service.generate_keyframe(db=db, request=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
