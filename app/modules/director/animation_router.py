from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from . import schemas, animation_service

router = APIRouter(tags=["Animation"])

@router.post("/generate-animation", response_model=schemas.AnimationResponse)
async def generate_animation(request: schemas.AnimationRequest, db: Session = Depends(get_db)):
    try:
        return await animation_service.generate_animation(db=db, request=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
