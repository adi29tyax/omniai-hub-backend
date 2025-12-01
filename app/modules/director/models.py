from sqlalchemy import Column, String, ForeignKey, Integer, Float, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class DirectorProject(Base):
    __tablename__ = "director_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stories = relationship("DirectorStory", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("DirectorAsset", back_populates="project", cascade="all, delete-orphan")

class DirectorStory(Base):
    __tablename__ = "director_stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("director_projects.id"), nullable=False)
    title = Column(String, nullable=False)
    logline = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    setting = Column(String, nullable=True)
    style = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("DirectorProject", back_populates="stories")
    characters = relationship("DirectorCharacter", back_populates="story", cascade="all, delete-orphan")
    scenes = relationship("DirectorScene", back_populates="story", cascade="all, delete-orphan")

class DirectorCharacter(Base):
    __tablename__ = "director_characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("director_stories.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    description = Column(String, nullable=True)
    personality = Column(String, nullable=True)
    visual_style = Column(String, nullable=True)
    voice_style = Column(String, nullable=True)

    story = relationship("DirectorStory", back_populates="characters")

class DirectorScene(Base):
    __tablename__ = "director_scenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("director_stories.id"), nullable=False)
    scene_id = Column(String, nullable=False) # e.g., "SC-001"
    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    location = Column(String, nullable=True)
    time_of_day = Column(String, nullable=True)

    story = relationship("DirectorStory", back_populates="scenes")
    shots = relationship("DirectorShot", back_populates="scene", cascade="all, delete-orphan")
    assets = relationship("DirectorAsset", back_populates="scene")

class DirectorShot(Base):
    __tablename__ = "director_shots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scene_id = Column(UUID(as_uuid=True), ForeignKey("director_scenes.id"), nullable=False)
    shot_id = Column(String, nullable=False) # e.g., "SH-001"
    type = Column(String, nullable=True)
    camera = Column(String, nullable=True)
    action = Column(String, nullable=True)
    prompt = Column(String, nullable=True)

    scene = relationship("DirectorScene", back_populates="shots")
    assets = relationship("DirectorAsset", back_populates="shot")

class DirectorAsset(Base):
    __tablename__ = "director_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("director_projects.id"), nullable=False)
    scene_id = Column(UUID(as_uuid=True), ForeignKey("director_scenes.id"), nullable=True)
    shot_id = Column(UUID(as_uuid=True), ForeignKey("director_shots.id"), nullable=True)
    
    type = Column(String, nullable=False) # image, video, audio, etc.
    url = Column(String, nullable=True) # url/path
    version = Column(Integer, default=1)
    metadata_ = Column("metadata", JSON, nullable=True)
    generation_settings = Column(JSON, nullable=True)
    composition_layers = Column(JSON, nullable=True)
    timeline_in = Column(Float, nullable=True)
    timeline_out = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("DirectorProject", back_populates="assets")
    scene = relationship("DirectorScene", back_populates="assets")
    shot = relationship("DirectorShot", back_populates="assets")
