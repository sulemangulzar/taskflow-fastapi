from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskPriority, TaskStatus


class CreateTask(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to_id: UUID | None = None
    due_date: datetime | None = None


class UpdateTask(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to_id: UUID | None = None
    due_date: datetime | None = None


class ReadTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: UUID
    created_by_id: UUID
    assigned_to_id: UUID | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
