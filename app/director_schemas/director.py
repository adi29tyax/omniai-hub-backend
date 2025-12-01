from pydantic import BaseModel
from typing import List, Optional


class CharacterBase(BaseModel):
    name: str
    visual_traits: Optional[str] = None
    reference_image_url: Optional[str] = None


class CharacterOut(CharacterBase):
    id: str
    class Config:
        from_attributes = True


class ShotBase(BaseModel):
    shot_number: int
    camera_angle: str
    subject: str
    action: Optional[str]
    visual_prompt: str
    dialogue: Optional[str]
    audio_mood: Optional[str]


class ShotOut(ShotBase):
    id: str
    keyframe_url: Optional[str]
    video_url: Optional[str]
    class Config:
        from_attributes = True


class SceneBase(BaseModel):
    scene_number: int
    location: str


class SceneOut(SceneBase):
    id: str
    shots: List[ShotOut] = []
    class Config:
        from_attributes = True


class StoryEngineRequest(BaseModel):
    project_id: str
    concept: str
    genre: str
    style_mode: str


class StoryEngineResponse(BaseModel):
    title: str
    logline: str
    characters: List[CharacterBase]
    scenes: List[SceneOut]
