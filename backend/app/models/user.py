from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlmodel import Field

from app.db.base import Base


class User(Base, table=True):
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    name: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
        ),
    )

    email: str = Field(
        sa_column=Column(
            String(320),
            nullable=False,
            unique=True,
            index=True,
        ),
    )

    hashed_password: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
        ),
    )
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )

    is_active: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=sa.true(),
        ),
    )

    is_verified: bool = Field(
        default=False,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
    )

    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
