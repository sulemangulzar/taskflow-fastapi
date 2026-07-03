from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field

from app.db.base import Base


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    BLOCKED = "blocked"
    DONE = "done"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base, table=True):
    __tablename__ = "tasks"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(nullable=False)
    description: str | None = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.TODO, nullable=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False)

    project_id: UUID = Field(foreign_key="projects.id", nullable=False)
    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    assigned_to_id: UUID | None = Field(default=None, foreign_key="users.id")

    due_date: datetime | None = Field(default=None)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.utcnow,
            nullable=False,
            onupdate=datetime.utcnow,
        )
    )
