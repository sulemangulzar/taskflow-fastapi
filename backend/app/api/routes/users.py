from fastapi import APIRouter, status

from app.api.dependencies import SessionDep
from app.schemas.auth import RegisterUser
from app.schemas.user import UserRead
from app.services.user import UserService

router = APIRouter(prefix="/auth/v1", tags=["Authentication"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(credentials: RegisterUser, session: SessionDep):
    return await UserService(session).create(credentials)
