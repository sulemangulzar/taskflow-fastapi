import asyncio
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import get_hashed_password, verify_password
from app.models.user import User
from app.repositories.token_repo import add_jti_to_blocklist
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterUser


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create(self, credentials: RegisterUser) -> User:
        existing_user = await self.repository.get_by_email(str(credentials.email))
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")

        hashed_pw = await asyncio.to_thread(get_hashed_password, credentials.password)
        user_role = "user"
        new_user = User(
            name=credentials.name,
            email=str(credentials.email),
            hashed_password=hashed_pw,
            role=user_role,
        )

        try:
            return await self.repository.create(new_user)
        except IntegrityError:
            await self.repository.rollback()
            raise HTTPException(status_code=409, detail="User already exists")

    async def login(self, email: str, password: str):
        if not email:
            raise HTTPException(status_code=400, detail="Email cannot be empty")

        user = await self.repository.get_by_email(str(email))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        is_valid = await asyncio.to_thread(
            verify_password, password, user.hashed_password
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id_str = str(user.id)
        access_token = create_access_token({"sub": user_id_str, "role": user.role})
        refresh_token = create_refresh_token({"sub": user_id_str, "role": user.role})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str):
        credentials_exception = HTTPException(
            status_code=401, detail="Invalid refresh token"
        )

        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise credentials_exception

        jti = payload.get("jti")

        user_id = payload.get("sub")
        if not jti or not user_id:
            raise credentials_exception
        exp = payload.get("exp")

        if not isinstance(jti, str) or not isinstance(exp, int) or not user_id:
            raise credentials_exception

        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise credentials_exception

        user = await self.repository.get_by_id(user_uuid)

        if not user or not user.is_active:
            raise credentials_exception

        await add_jti_to_blocklist(jti, exp)

        user_id_str = str(user.id)
        new_access_token = create_access_token({"sub": user_id_str, "role": user.role})
        new_refresh_token = create_refresh_token(
            {"sub": user_id_str, "role": user.role}
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def logout(self, token: str):
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        await add_jti_to_blocklist(jti, exp)

        return {"message": "Successfully logged out"}
