from pydantic import BaseModel

class ProjectBase(BaseModel):
    name: str
    description: str | None = None

class ProjectOut(ProjectBase):
    id: int
    org_id: int
    created_by: int

    class Config:
        from_attributes = True
