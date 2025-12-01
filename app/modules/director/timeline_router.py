from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from . import schemas, timeline_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Timeline"])

@router.post("/compile-episode", response_model=schemas.TimelineResponse)
async def compile_episode(request: schemas.TimelineRequest, db: Session = Depends(get_db)):
    try:
        return await timeline_service.compile_episode(db=db, request=request)
    except Exception as e:
        logger.error(f"Compile Episode Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
