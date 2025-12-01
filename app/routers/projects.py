from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project, User
from app.schemas.project import ProjectBase, ProjectOut
from app.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    items = (
        db.query(Project)
        .filter(Project.org_id == user.org_id)
        .order_by(Project.id.desc())
        .all()
    )
    return items


@router.post("/", response_model=ProjectOut)
def create_project(
    payload: ProjectBase,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    pr = Project(
        org_id=user.org_id,
        name=payload.name,
        description=payload.description,
        created_by=user.id,
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    pr = (
        db.query(Project)
        .filter(Project.id == project_id, Project.org_id == user.org_id)
        .first()
    )
    if not pr:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(pr)
    db.commit()
    return {"ok": True, "message": "Project deleted successfully"}
