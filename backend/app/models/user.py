from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy.dialects.postgresql as pg
from pydantic import EmailStr
from sqlmodel import Field, SQLModel,Column

# Assuming app/db/base.py has: Base = SQLModel
from app.db.base import Base

class User(Base, table=True):
    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, nullable=False)
    )

    name: str = Field(nullable=False)

    email: EmailStr = Field(
        nullable=False,
        unique=True,
        index=True
    )

    hashed_password: str = Field(nullable=False)

    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP(timezone=True)
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            onupdate=datetime.utcnow #
        )
    )
