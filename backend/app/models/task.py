from typing import TYPE_CHECKING
from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.models.projects import Project

from sqlmodel import Relationship
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import String, func
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

    title: str = Field(
        sa_column=Column(String, nullable=False)
    )

    description: str | None = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )

    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        sa_column=Column(
            sa.Enum(
                *[s.value for s in TaskStatus],
                name="taskstatus",
            ),
            nullable=False,
            server_default=TaskStatus.TODO.value,
        ),
    )

    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        sa_column=Column(
            sa.Enum(
                *[p.value for p in TaskPriority],
                name="taskpriority",
            ),
            nullable=False,
            server_default=TaskPriority.MEDIUM.value,
        ),
    )

    project_id: UUID = Field(foreign_key="projects.id", nullable=False)
    created_by_id: UUID = Field(foreign_key="users.id", nullable=False)
    assigned_to_id: UUID | None = Field(default=None, foreign_key="users.id")

    # Stored as plain string (email); nullable since assignment is optional
    assigned_to_email: str | None = Field(
        default=None,
        sa_column=Column(String(320), nullable=True),
    )

    due_date: date | None = Field(
        default=None, sa_column=Column(pg.DATE, nullable=True)
    )

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    project: "Project" = Relationship(back_populates="tasks")