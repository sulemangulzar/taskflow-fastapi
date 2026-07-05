from typing import TYPE_CHECKING
from datetime import datetime, timezone
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.models.task import Task

from sqlmodel import Relationship

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import String, func
from sqlmodel import Column, Field

from app.db.base import Base


class Project(Base, table=True):
    __tablename__ = "projects"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    description: str = Field(
        sa_column=Column(String, nullable=False)
    )

    owner_id: UUID = Field(foreign_key="users.id", nullable=False)

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

    tasks : list["Task"] = Relationship(
        back_populates="project",
        cascade_delete=True,)