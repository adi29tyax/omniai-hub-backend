from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.deps import get_current_user
from . import schemas, service

router = APIRouter(
    tags=["director"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# Projects
@router.post("/projects/create", response_model=schemas.DirectorProjectResponse)
def create_project(project: schemas.DirectorProjectCreate, db: Session = Depends(get_db)):
    return service.create_project(db=db, project=project)

@router.get("/projects/list/{user_id}", response_model=List[schemas.DirectorProjectResponse])
def list_projects(user_id: str, db: Session = Depends(get_db)):
    return service.get_projects_by_user(db=db, user_id=user_id)

@router.get("/projects/get/{project_id}", response_model=schemas.DirectorProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    db_project = service.get_project(db=db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/projects/delete/{project_id}", response_model=schemas.DirectorProjectResponse)
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    db_project = service.delete_project(db=db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# Story
@router.post("/story/create", response_model=schemas.DirectorStoryResponse)
def create_story(story: schemas.DirectorStoryCreate, db: Session = Depends(get_db)):
    return service.create_story(db=db, story=story)

@router.get("/story/get/{story_id}", response_model=schemas.DirectorStoryResponse)
def get_story(story_id: UUID, db: Session = Depends(get_db)):
    db_story = service.get_story(db=db, story_id=story_id)
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return db_story

# Scenes
@router.post("/scenes/create", response_model=schemas.SceneResponse)
def create_scene(scene: schemas.SceneCreate, db: Session = Depends(get_db)):
    return service.create_scene(db=db, scene=scene)

@router.get("/scenes/list/{story_id}", response_model=List[schemas.SceneResponse])
def list_scenes(story_id: UUID, db: Session = Depends(get_db)):
    return service.get_scenes_by_story(db=db, story_id=story_id)

# Shots
@router.post("/shots/create", response_model=schemas.ShotResponse)
def create_shot(shot: schemas.ShotCreate, db: Session = Depends(get_db)):
    return service.create_shot(db=db, shot=shot)

@router.get("/shots/list/{scene_id}", response_model=List[schemas.ShotResponse])
def list_shots(scene_id: UUID, db: Session = Depends(get_db)):
    return service.get_shots_by_scene(db=db, scene_id=scene_id)

# Assets
@router.post("/assets/create", response_model=schemas.AssetResponse)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    return service.create_asset(db=db, asset=asset)

@router.get("/assets/list/{project_id}", response_model=List[schemas.AssetResponse])
def list_assets(project_id: UUID, db: Session = Depends(get_db)):
    return service.get_assets_by_project(db=db, project_id=project_id)

@router.get("/assets/by-scene/{scene_id}", response_model=List[schemas.AssetResponse])
def list_assets_by_scene(scene_id: UUID, db: Session = Depends(get_db)):
    return service.get_assets_by_scene(db=db, scene_id=scene_id)

@router.get("/assets/by-shot/{shot_id}", response_model=List[schemas.AssetResponse])
def list_assets_by_shot(shot_id: UUID, db: Session = Depends(get_db)):
    return service.get_assets_by_shot(db=db, shot_id=shot_id)

@router.delete("/assets/delete/{asset_id}", response_model=schemas.AssetResponse)
def delete_asset(asset_id: UUID, db: Session = Depends(get_db)):
    db_asset = service.delete_asset(db=db, asset_id=asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset
