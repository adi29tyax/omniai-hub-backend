from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

from app.database import get_db
from . import auto_director_service, schemas

router = APIRouter(tags=["Auto Director"])

class AutoEpisodeRequest(BaseModel):
    project_id: UUID
    concept: str
    style: str
    duration: int = 5 # minutes

class AutoEpisodeResponse(BaseModel):
    message: str
    episode_url: Optional[str] = None
    logs: List[str]

class AutoStoryRequest(BaseModel):
    project_id: UUID
    concept: str
    style: str
    duration: int = 5

@router.post("/generate-story", response_model=schemas.DirectorStoryResponse)
async def generate_story(request: AutoStoryRequest, db: Session = Depends(get_db)):
    try:
        story = await auto_director_service.generate_story(
            db,
            request.project_id,
            request.concept,
            request.style,
            request.duration
        )
        return story
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-episode", response_model=AutoEpisodeResponse)
async def generate_episode(request: AutoEpisodeRequest, db: Session = Depends(get_db)):
    """
    Trigger the Auto-Director to generate a full episode from scratch.
    WARNING: This is a long-running process.
    """
    try:
        # In a real production app, this should be a background task (Celery/Redis Queue).
        # For this prototype, we'll await it (blocking) or use FastAPI BackgroundTasks if we want async.
        # Given the requirement "Returns playable episode URL", it implies we wait for it?
        # Or maybe we return a job ID.
        # The user request says: "Returns playable episode URL" in the response.
        # So we will await it.
        
        result = await auto_director_service.generate_full_episode(
            db,
            request.project_id,
            request.concept,
            request.style,
            request.duration
        )
        
        return AutoEpisodeResponse(
            message="Episode generated successfully",
            episode_url=result["episode_url"],
            logs=result["logs"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
