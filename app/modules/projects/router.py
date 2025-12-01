from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from .schema import ProjectCreate, ProjectUpdate, ProjectResponse
from .service import create_project, list_projects, get_project, update_project, delete_project

router = APIRouter(tags=["Projects"])

@router.post("/create", response_model=ProjectResponse)
async def create_project_api(data: ProjectCreate, db: Session = Depends(get_db)):
    return await create_project(db, data)

@router.get("/list/{user_id}", response_model=List[ProjectResponse])
async def list_projects_api(user_id: str, db: Session = Depends(get_db)):
    return await list_projects(db, user_id)

@router.get("/get/{project_id}", response_model=ProjectResponse)
async def get_project_api(project_id: UUID, db: Session = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/update/{project_id}", response_model=ProjectResponse)
async def update_project_api(project_id: UUID, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = await update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/delete/{project_id}")
async def delete_project_api(project_id: UUID, db: Session = Depends(get_db)):
    success = await delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}
