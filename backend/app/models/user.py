from datetime import UTC, datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field

from app.db.base import Base


class User(Base, table=True):
    __tablename__ = "users"  # type: ignore

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
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

    is_active: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            nullable=False,
            default=True,
            server_default=sa.true(),
        ),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
