from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateProject(BaseModel):
    name: str
    description: str


class UpdateProject(BaseModel):
    name: str | None = None
    description: str | None = None


class ReadProject(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
