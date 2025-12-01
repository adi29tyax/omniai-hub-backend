from sqlalchemy.orm import Session
from .models import IDEProject
from .schema import ProjectCreate, ProjectUpdate
import uuid

async def create_project(db: Session, data: ProjectCreate):
    project = IDEProject(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

async def list_projects(db: Session, user_id: str):
    return db.query(IDEProject).filter(IDEProject.user_id == user_id).all()

async def get_project(db: Session, project_id: uuid.UUID):
    return db.query(IDEProject).filter(IDEProject.id == project_id).first()

async def update_project(db: Session, project_id: uuid.UUID, data: ProjectUpdate):
    project = db.query(IDEProject).filter(IDEProject.id == project_id).first()
    if not project:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project

async def delete_project(db: Session, project_id: uuid.UUID):
    project = db.query(IDEProject).filter(IDEProject.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
        return True
    return False
