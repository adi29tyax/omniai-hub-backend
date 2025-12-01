from fastapi import APIRouter, HTTPException
from . import schemas, assistant_service

router = APIRouter(tags=["AI Assistant"])

@router.post("/query", response_model=schemas.AssistantResponse)
async def query_assistant(request: schemas.AssistantRequest):
    try:
        return await assistant_service.process_query(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
