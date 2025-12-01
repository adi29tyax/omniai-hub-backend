from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from app.modules.director.animation_engine import generate_animation_blocks
from app.deps import get_current_user
from app.models import User

router = APIRouter()

class AnimationRequest(BaseModel):
    keyframes: List[Dict[str, Any]]
    shot_metadata: Dict[str, Any] = {}

@router.post("/generate")
async def generate_animation(
    payload: AnimationRequest,
    user: User = Depends(get_current_user)
):
    try:
        # Convert Pydantic model to dict
        payload_dict = payload.model_dump()
        blocks = await generate_animation_blocks(payload_dict, user)
        return {"animation_blocks": blocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
