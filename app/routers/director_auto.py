from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.modules.director.auto_director import auto_direct_episode
from app.deps import get_current_user
from app.models import User

router = APIRouter()

class AutoDirectorRequest(BaseModel):
    story: str
    title: Optional[str] = "Untitled Episode"
    resolution: Optional[str] = "1920x1080"
    fps: Optional[int] = 24

@router.post("/create")
async def create_episode(
    payload: AutoDirectorRequest,
    user: User = Depends(get_current_user)
):
    try:
        # Convert Pydantic model to dict
        payload_dict = payload.model_dump()
        result = await auto_direct_episode(payload_dict, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
