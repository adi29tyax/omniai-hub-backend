from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.modules.director.scene_breakdown import generate_scene_breakdown

router = APIRouter(tags=["Director - Scene Breakdown"])

class SceneRequest(BaseModel):
    story_text: str

@router.post("/breakdown")
async def scene_breakdown(payload: SceneRequest):
    try:
        scenes = await generate_scene_breakdown(payload.story_text)
        return {"scenes": scenes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
