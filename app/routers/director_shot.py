from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from app.modules.director.shot_breakdown import generate_shot_breakdown

router = APIRouter(tags=["Director - Shot Breakdown"])

class ShotRequest(BaseModel):
    scene: Dict[str, Any]

@router.post("/breakdown")
async def shot_breakdown(payload: ShotRequest):
    try:
        shots = await generate_shot_breakdown(payload.scene)
        return {"shots": shots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
