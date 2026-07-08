import asyncio
from uuid import UUID

from fastapi import BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_tasks import send_email
from app.core.config import settings
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import get_hashed_password, verify_password
from app.core.utils import create_url_safe_token, decode_url_safe_token
from app.errors import (
    EmailAlreadyExistsError,
    InputValidationError,
    InvalidCredentialsError,
    InvalidToken,
    PasswordResetNotMatching,
)
from app.models.user import User
from app.repositories.token_repo import add_jti_to_blocklist
from app.repositories.user import UserRepository
from app.schemas.auth import PasswordResetConfirm, RegisterUser


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create(self, credentials: RegisterUser, bg_task: BackgroundTasks) -> User:
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
            recipients = [str(credentials.email)]
            subject = "Welcome to TaskFlow"
            body = html_template

            send_email.delay(recipients, subject, body)  # type: ignore[attr-defined]
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

    async def logout(self, access_token: str, refresh_token: str | None = None):
        # Block access token
        payload = decode_token(access_token)
        if not payload:
            raise InvalidToken("Invalid token")
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not jti or not exp:
            raise InvalidToken("Invalid token payload")
        await add_jti_to_blocklist(jti, exp)

        # Block refresh token if provided
        if refresh_token:
            rt_payload = decode_token(refresh_token)
            if rt_payload:
                rt_jti = rt_payload.get("jti")
                rt_exp = rt_payload.get("exp")
                if rt_jti and rt_exp:
                    await add_jti_to_blocklist(rt_jti, rt_exp)

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

    async def reset_password(self, email: EmailStr, bg_task: BackgroundTasks):
        try:
            user = await self.repository.get_by_email(str(email))
            if not user:
                return JSONResponse(
                    content={
                        "message": "Please Check Your Email To Reset Your Password"
                    },
                    status_code=status.HTTP_200_OK,
                )

            url_safe_token = create_url_safe_token({"email": str(email)})
            link = f"http://{settings.DOMAIN}/auth/v1/reset-password/{url_safe_token}"
            html_template = f"""
            <h2>Password Reset</h2>
            <p>Click below to reset your password</p>
            <a href="{link}">Verify email</a>
            <p>This link expires in 30 minutes.</p>
            """
            recipients = [str(email)]
            subject = "Welcome to TaskFlow"
            body = html_template

            send_email.delay(recipients, subject, body)  # type: ignore[attr-defined]
            return JSONResponse(
                content={"message": "Please Check Your Email To Reset Your Password"},
                status_code=status.HTTP_200_OK,
            )

        except Exception:
            return JSONResponse(
                content={"message": "An error occurred"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def reset_password_confirm(self, token: str, new_creds: PasswordResetConfirm):
        if new_creds.new_password != new_creds.confirm_new_password:
            raise PasswordResetNotMatching()

        token_data = decode_url_safe_token(token)
        if not token_data or "email" not in token_data:
            raise InvalidToken("Invalid or expired password reset token")

        email = token_data["email"]
        user = await self.repository.get_by_email(email)
        if not user:
            raise InputValidationError("User not found")

        hashed_password = await asyncio.to_thread(
            get_hashed_password, new_creds.new_password
        )
        user.hashed_password = hashed_password

        await self.repository.update(user)

        return {"message": "Password successfully reset"}
