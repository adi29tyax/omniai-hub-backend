from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
from app.worker.renderer import generate_video_from_timeline
from app.deps import get_current_user
from app.models import User

router = APIRouter()

# Simple in-memory status tracker (for demonstration/MVP)
# In production, use Redis or DB
RENDER_TASKS: Dict[str, Dict[str, Any]] = {}

class RenderRequest(BaseModel):
    timeline: Dict[str, Any]
    project_id: Optional[str] = None

async def run_render_task(task_id: str, timeline_data: Dict[str, Any]):
    RENDER_TASKS[task_id] = {"status": "processing"}
    try:
        result = await generate_video_from_timeline(timeline_data)
        RENDER_TASKS[task_id] = result
    except Exception as e:
        RENDER_TASKS[task_id] = {"status": "failed", "error": str(e)}

@router.post("/video")
async def start_render(
    payload: RenderRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    task_id = str(uuid.uuid4())
    RENDER_TASKS[task_id] = {"status": "queued"}
    
    # Pass the timeline data to the background task
    background_tasks.add_task(run_render_task, task_id, payload.timeline)
    
    return {"task_id": task_id, "status": "queued"}

@router.get("/status/{task_id}")
async def get_render_status(task_id: str, user: User = Depends(get_current_user)):
    task = RENDER_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
