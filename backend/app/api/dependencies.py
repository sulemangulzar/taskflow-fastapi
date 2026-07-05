from app.errors import AccountNotVerified
from app.errors import ForbiddenError
from app.errors import InvalidTokenType
from app.errors import UserNotFoundOrUnauthorised
from app.errors import InvalidToken
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_token
from app.db.session import get_session
from app.models.user import User
from app.repositories.token_repo import token_in_blocklist
from app.repositories.user import UserRepository
from app.services.project import ProjectService
from app.services.task import TaskService
from app.services.user import UserService

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/v1/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDep):
    return UserService(session)


def get_project_service(session: SessionDep):
    return ProjectService(session)


def get_task_service(session: SessionDep):
    return TaskService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)], session: SessionDep
) -> User:

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise InvalidTokenType()

    jti = payload.get("jti")
    user_id = payload.get("sub")

    if not isinstance(jti, str) or not isinstance(user_id, str):
        raise InvalidToken()

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise InvalidToken()

    if await token_in_blocklist(jti):
        raise InvalidToken()

    repo = UserRepository(session)
    user = await repo.get_by_id(user_uuid)

    if not user or not user.is_active:
        raise UserNotFoundOrUnauthorised()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUserDep) -> bool:
        user_role = getattr(current_user, "role", None)
        if not current_user.is_verified:
            raise AccountNotVerified()
        if user_role in self.allowed_roles:
            return True

        raise ForbiddenError()
