from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from app.modules.director.keyframe_generator import generate_keyframes

router = APIRouter()

class KeyframeRequest(BaseModel):
    shot: Dict

@router.post("/generate")
async def keyframe_generate(payload: KeyframeRequest):
    keyframes = await generate_keyframes(payload.shot)
    return {"keyframes": keyframes}
