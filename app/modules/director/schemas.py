from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Project
class DirectorProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class DirectorProjectCreate(DirectorProjectBase):
    user_id: str

class DirectorProjectResponse(DirectorProjectBase):
    id: UUID
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Story
class DirectorStoryBase(BaseModel):
    title: str
    logline: Optional[str] = None
    theme: Optional[str] = None
    setting: Optional[str] = None
    style: Optional[str] = None

class DirectorStoryCreate(DirectorStoryBase):
    project_id: UUID

class DirectorStoryResponse(DirectorStoryBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Character
class CharacterBase(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None
    visual_style: Optional[str] = None
    voice_style: Optional[str] = None

class CharacterCreate(CharacterBase):
    story_id: UUID

class CharacterResponse(CharacterBase):
    id: UUID
    story_id: UUID

    class Config:
        from_attributes = True

# Scene
class SceneBase(BaseModel):
    scene_id: str
    title: str
    summary: Optional[str] = None
    location: Optional[str] = None
    time_of_day: Optional[str] = None

class SceneCreate(SceneBase):
    story_id: UUID

class SceneResponse(SceneBase):
    id: UUID
    story_id: UUID

    class Config:
        from_attributes = True

# Shot
class ShotBase(BaseModel):
    shot_id: str
    type: Optional[str] = None
    camera: Optional[str] = None
    action: Optional[str] = None
    prompt: Optional[str] = None

class ShotCreate(ShotBase):
    scene_id: UUID

class ShotResponse(ShotBase):
    id: UUID
    scene_id: UUID

    class Config:
        from_attributes = True

# Asset
class AssetBase(BaseModel):
    type: str
    url: Optional[str] = None
    version: Optional[int] = 1
    metadata: Optional[Dict[str, Any]] = None
    generation_settings: Optional[Dict[str, Any]] = None
    composition_layers: Optional[Dict[str, Any]] = None
    timeline_in: Optional[float] = None
    timeline_out: Optional[float] = None

class AssetCreate(AssetBase):
    project_id: UUID
    scene_id: Optional[UUID] = None
    shot_id: Optional[UUID] = None

class AssetResponse(AssetBase):
    id: UUID
    project_id: UUID
    scene_id: Optional[UUID] = None
    shot_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Breakdown
class SceneBreakdownRequest(BaseModel):
    story_id: UUID
    scene_id: UUID
    style: str
    override_concept: Optional[str] = None

class ShotBreakdownItem(BaseModel):
    shot_id: str
    type: str
    lens: str
    camera_movement: str
    environment: str
    lighting: str
    action: str
    emotion: str
    color_palette: str
    transition: str
    prompt: str

class ShotBreakdownResponse(BaseModel):
    scene_id: UUID
    shots: List[ShotBreakdownItem]

# Keyframe
class KeyframeRequest(BaseModel):
    project_id: UUID
    scene_id: UUID
    shot_id: UUID
    style: str
    override_prompt: Optional[str] = None

class KeyframeResponse(BaseModel):
    asset_id: UUID
    url: Optional[str]
    version: int
    metadata: Optional[Dict[str, Any]] = None
    generation_settings: Optional[Dict[str, Any]] = None

# Animation
class AnimationRequest(BaseModel):
    project_id: UUID
    scene_id: UUID
    shot_id: UUID
    model: str # "luma" | "pika" | "runway" | "kling" | "animatediff"
    duration: float
    override_prompt: Optional[str] = None

class AnimationResponse(BaseModel):
    asset_id: UUID
    url: Optional[str]
    version: int
    metadata: Optional[Dict[str, Any]] = None
    generation_settings: Optional[Dict[str, Any]] = None

# Audio
class AudioRequest(BaseModel):
    project_id: UUID
    scene_id: UUID
    shot_id: Optional[UUID] = None
    character_id: Optional[UUID] = None
    text: str
    emotion: Optional[str] = None
    style: Optional[str] = None

class AudioResponse(BaseModel):
    asset_id: UUID
    url: Optional[str]
    metadata: Optional[Dict[str, Any]] = None

class SfxRequest(BaseModel):
    project_id: UUID
    scene_id: UUID
    shot_id: UUID
    action_description: Optional[str] = None

class BgmRequest(BaseModel):
    project_id: UUID
    scene_id: UUID
    mood: Optional[str] = None
    pacing: Optional[str] = None

# Timeline
class TimelineRequest(BaseModel):
    project_id: UUID
    episode_title: str
    scene_order: List[UUID]

class TimelineResponse(BaseModel):
    asset_id: UUID
    url: Optional[str]
    metadata: Optional[Dict[str, Any]] = None
