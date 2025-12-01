from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from uuid import UUID
from app.database import get_db
from .schema import FileCreate, FileUpdate, FileResponse
from .service import create_file, update_file, get_file, delete_file, list_files, build_tree

router = APIRouter(tags=["Project Files"])

@router.post("/create", response_model=FileResponse)
async def create_file_api(data: FileCreate, db: Session = Depends(get_db)):
    return await create_file(db, data)

@router.put("/update/{file_id}", response_model=FileResponse)
async def update_file_api(file_id: UUID, data: FileUpdate, db: Session = Depends(get_db)):
    file = await update_file(db, file_id, data)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.get("/get/{file_id}", response_model=FileResponse)
async def get_file_api(file_id: UUID, db: Session = Depends(get_db)):
    file = await get_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.delete("/delete/{file_id}")
async def delete_file_api(file_id: UUID, db: Session = Depends(get_db)):
    success = await delete_file(db, file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}

@router.get("/list/{project_id}", response_model=List[FileResponse])
async def list_files_api(project_id: UUID, db: Session = Depends(get_db)):
    return await list_files(db, project_id)

@router.get("/tree/{project_id}")
async def get_tree_api(project_id: UUID, db: Session = Depends(get_db)):
    return await build_tree(db, project_id)
