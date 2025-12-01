from fastapi import APIRouter
from .schema import CodeRequest, RunRequest
from .service import generate_code, debug_code, explain_code
from .executor import run_python_code

router = APIRouter(prefix="/ide", tags=["IDE"])

@router.post("/generate")
async def generate_code_api(request: CodeRequest):
    return await generate_code(request)

@router.post("/debug")
async def debug_code_api(request: CodeRequest):
    return await debug_code(request)

@router.post("/explain")
async def explain_code_api(request: CodeRequest):
    return await explain_code(request)

@router.post("/run")
async def run_code_api(request: RunRequest):
    output = run_python_code(request.code)
    return {"output": output}
