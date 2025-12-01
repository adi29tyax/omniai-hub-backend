from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from . import models, schemas

# Project
def create_project(db: Session, project: schemas.DirectorProjectCreate):
    db_project = models.DirectorProject(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_by_user(db: Session, user_id: str):
    return db.query(models.DirectorProject).filter(models.DirectorProject.user_id == user_id).all()

def get_project(db: Session, project_id: UUID):
    return db.query(models.DirectorProject).filter(models.DirectorProject.id == project_id).first()

def delete_project(db: Session, project_id: UUID):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

# Story
def create_story(db: Session, story: schemas.DirectorStoryCreate):
    db_story = models.DirectorStory(**story.model_dump())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

def get_story(db: Session, story_id: UUID):
    return db.query(models.DirectorStory).filter(models.DirectorStory.id == story_id).first()

# Character
def create_character(db: Session, character: schemas.CharacterCreate):
    db_character = models.DirectorCharacter(**character.model_dump())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def get_characters_by_story(db: Session, story_id: UUID):
    # This wasn't explicitly requested in the router list but is useful/implied by "CRUD services for Characters"
    return db.query(models.DirectorCharacter).filter(models.DirectorCharacter.story_id == story_id).all()

# Scene
def create_scene(db: Session, scene: schemas.SceneCreate):
    db_scene = models.DirectorScene(**scene.model_dump())
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    return db_scene

def get_scenes_by_story(db: Session, story_id: UUID):
    return db.query(models.DirectorScene).filter(models.DirectorScene.story_id == story_id).all()

# Shot
def create_shot(db: Session, shot: schemas.ShotCreate):
    db_shot = models.DirectorShot(**shot.model_dump())
    db.add(db_shot)
    db.commit()
    db.refresh(db_shot)
    return db_shot

def get_shots_by_scene(db: Session, scene_id: UUID):
    return db.query(models.DirectorShot).filter(models.DirectorShot.scene_id == scene_id).all()

# Asset
def create_asset(db: Session, asset: schemas.AssetCreate):
    # Handle the metadata field mapping if necessary, but Pydantic model_dump should match the kwargs.
    # However, in models.py I used `metadata_` as the attribute name.
    # So I need to map `metadata` from schema to `metadata_` in model.
    asset_data = asset.model_dump()
    if 'metadata' in asset_data:
        asset_data['metadata_'] = asset_data.pop('metadata')
    
    db_asset = models.DirectorAsset(**asset_data)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def get_assets_by_project(db: Session, project_id: UUID):
    return db.query(models.DirectorAsset).filter(models.DirectorAsset.project_id == project_id).all()

def get_assets_by_scene(db: Session, scene_id: UUID):
    return db.query(models.DirectorAsset).filter(models.DirectorAsset.scene_id == scene_id).all()

def get_assets_by_shot(db: Session, shot_id: UUID):
    return db.query(models.DirectorAsset).filter(models.DirectorAsset.shot_id == shot_id).all()

def delete_asset(db: Session, asset_id: UUID):
    db_asset = db.query(models.DirectorAsset).filter(models.DirectorAsset.id == asset_id).first()
    if db_asset:
        db.delete(db_asset)
        db.commit()
    return db_asset
