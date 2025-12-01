from pydantic import BaseModel

class CodeRequest(BaseModel):
    prompt: str
    language: str = "python"

class RunRequest(BaseModel):
    code: str
