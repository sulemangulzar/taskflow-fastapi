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

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    jti = payload.get("jti")
    user_id = payload.get("sub")

    if not isinstance(jti, str) or not isinstance(user_id, str):
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    if await token_in_blocklist(jti):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_uuid)

    if not user or not user.is_active:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUserDep) -> bool:
        user_role = getattr(current_user, "role", None)

        if user_role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )
