from sqlalchemy import Column, String, Integer, Text, ForeignKey, BigInteger, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    visual_traits = Column(Text, nullable=True)
    reference_image_url = Column(String, nullable=True)

    project = relationship("Project", back_populates="characters")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    scene_number = Column(Integer, nullable=False)
    location = Column(String, nullable=False)

    project = relationship("Project", back_populates="scenes")
    shots = relationship("Shot", back_populates="scene")


class Shot(Base):
    __tablename__ = "shots"

    id = Column(String, primary_key=True, index=True)
    scene_id = Column(String, ForeignKey("scenes.id"))
    shot_number = Column(Integer, nullable=False)

    # AI-directive fields
    camera_angle = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    action = Column(Text, nullable=True)
    visual_prompt = Column(Text, nullable=False)

    dialogue = Column(Text, nullable=True)
    audio_mood = Column(String, nullable=True)

    # ML fields (for diffusion models)
    seed = Column(BigInteger, nullable=True)
    cfg_scale = Column(Float, nullable=True)

    # Assets
    keyframe_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    voice_audio_url = Column(String, nullable=True)

    # Consistency reference
    consistency_ref = Column(String, nullable=True)

    scene = relationship("Scene", back_populates="shots")
