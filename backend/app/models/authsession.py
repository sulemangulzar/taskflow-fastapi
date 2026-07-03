from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field

from app.db.base import Base


class AuthSession(Base, table=True):
    __tablename__ = "auth_sessions"  # type: ignore

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )

    refresh_token_hash: str = Field(
        sa_column=Column(
            String(64),
            nullable=False,
            unique=True,
            index=True,
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

    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )
