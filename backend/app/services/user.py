from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hashed_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterUser


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create(self, credentials: RegisterUser) -> User:
        existing_user = await self.repository.get_by_email(str(credentials.email))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

        new_user = User(
            name=credentials.name,
            email=str(credentials.email),
            hashed_password=get_hashed_password(credentials.password),
        )

        try:
            return await self.repository.create(new_user)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            ) from exc
