from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.modules.director.timeline_compiler import compile_timeline
from app.deps import get_current_user
from app.models import User

router = APIRouter()

class TimelineCompileRequest(BaseModel):
    scenes: List[Dict[str, Any]] = []
    audio_layers: List[Dict[str, Any]] = []
    resolution: str = "1920x1080"
    fps: int = 24
    project_id: str | None = None

@router.post("/compile")
async def compile_timeline_endpoint(
    payload: TimelineCompileRequest,
    user: User = Depends(get_current_user)
):
    try:
        # Convert Pydantic model to dict
        payload_dict = payload.model_dump()
        result = await compile_timeline(payload_dict, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
