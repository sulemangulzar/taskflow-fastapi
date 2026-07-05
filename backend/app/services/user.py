from email_validator import validate_email
from app.mail import create_message
from email_validator import validate_email
from anyio import lowlevel
from app.core.utils import create_url_safe_token, decode_url_safe_token
import asyncio
from uuid import UUID
from app.mail import mail
from app.errors import (
    EmailAlreadyExistsError,
    InputValidationError,
    InvalidCredentialsError,
    InvalidToken,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
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
            raise EmailAlreadyExistsError()

        hashed_pw = await asyncio.to_thread(get_hashed_password, credentials.password)
        user_role = "user"
        new_user = User(
            name=credentials.name,
            email=str(credentials.email),
            hashed_password=hashed_pw,
            role=user_role,
        )

        try:
            url_safe_token = create_url_safe_token({"email": str(credentials.email)})
            link = f"http://{settings.DOMAIN}/auth/v1/verify/{url_safe_token}"
            html_template = f"""
            <h2>Email verification</h2>
            <p>Click below to verify your account:</p>
            <a href="{link}">Verify email</a>
            <p>This link expires in 30 minutes.</p>
            """
            message = create_message(
                recipients=[str(credentials.email)],
                subject="Welcome to TaskFlow",
                body=html_template
            )
            await mail.send_message(message)
            return await self.repository.create(new_user)
        except IntegrityError:
            await self.repository.rollback()
            raise EmailAlreadyExistsError()

    async def login(self, email: str, password: str):
        if not email:
            raise InputValidationError("Email cannot be empty")

        user = await self.repository.get_by_email(str(email))
        if not user:
            raise InvalidCredentialsError()

        is_valid = await asyncio.to_thread(
            verify_password, password, user.hashed_password
        )
        if not is_valid:
            raise InvalidCredentialsError()

        user_id_str = str(user.id)
        access_token = create_access_token({"sub": user_id_str, "role": user.role})
        refresh_token = create_refresh_token({"sub": user_id_str, "role": user.role})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str):
        credentials_exception = InvalidToken("Invalid refresh token")

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
            raise InvalidToken("Invalid token")

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            raise InvalidToken("Invalid token payload")
        await add_jti_to_blocklist(jti, exp)

        return {"message": "Successfully logged out"}

    async def verify_email(self, token: str):
        token_data = decode_url_safe_token(token)
        if not token_data or "email" not in token_data:
            raise InvalidToken("Invalid or expired verification token")
        
        email = token_data["email"]
        user = await self.repository.get_by_email(email)
        if not user:
            raise InputValidationError("User not found")
        
        if user.is_verified:
            return {"message": "Email is already verified"}
            
        user.is_verified = True
        await self.repository.update(user)
        
        return {"message": "Email successfully verified"}
