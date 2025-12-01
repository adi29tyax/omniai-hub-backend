from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from . import schemas, breakdown_service

router = APIRouter(
    tags=["director-breakdown"],
    responses={404: {"description": "Not found"}},
)

@router.post("/breakdown-scene", response_model=schemas.ShotBreakdownResponse)
async def breakdown_scene(request: schemas.SceneBreakdownRequest, db: Session = Depends(get_db)):
    try:
        return await breakdown_service.breakdown_scene(db=db, request=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
