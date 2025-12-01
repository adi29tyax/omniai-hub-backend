from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

class AssistantRequest(BaseModel):
    mode: str # "global" | "scene" | "shot" | "keyframe" | "animation" | "audio" | "timeline"
    context: Dict[str, Any]
    message: str
    project_id: Optional[UUID] = None

class AssistantAction(BaseModel):
    label: str
    action: str
    payload: Optional[Dict[str, Any]] = None

class AssistantResponse(BaseModel):
    response: str
    actions: List[AssistantAction] = []
    metadata_fixes: Optional[Dict[str, Any]] = None
    improved_prompt: Optional[str] = None
