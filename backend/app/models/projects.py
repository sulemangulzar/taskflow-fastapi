from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field

from app.db.base import Base


class Project(Base, table=True):
    __tablename__ = "projects"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field()
    owner_id: UUID = Field(foreign_key="users.id", nullable=False)
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
