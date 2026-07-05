from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    @field_validator("due_date", mode="before", check_fields=False)
    @classmethod
    def parse_due_date(cls, value):
        if value is None or isinstance(value, date):
            return value

        if isinstance(value, str) and "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()

        return value


class CreateTask(TaskBase):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to_email: EmailStr | None = None
    due_date: date | None = None


class UpdateTask(TaskBase):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to_email: EmailStr | None = None
    due_date: date | None = None


class ReadTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: UUID
    created_by_id: UUID
    assigned_to_id: UUID | None = None
    assigned_to_email: str | None = None
    due_date: date | None
    created_at: datetime
    updated_at: datetime
