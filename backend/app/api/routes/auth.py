from fastapi import APIRouter, Body, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    RoleChecker,
    UserServiceDep,
    get_current_user,
    oauth_scheme,
)
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, RegisterUser, TokenResponse, UserRead

router = APIRouter(prefix="/auth/v1", tags=["Authentication"])
role_checker = RoleChecker(["admin", "user"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(credentials: RegisterUser, service: UserServiceDep):
    return await service.create(credentials)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(credentials: RegisterUser, service: UserServiceDep):
    return await service.create(credentials)


@router.post("/login", response_model=TokenResponse)
async def login(
    service: UserServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await service.login(form_data.username, form_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    service: UserServiceDep,
    data: RefreshTokenRequest = Body(
        examples=[{"refresh_token": "paste-your-refresh-token-here"}]
    ),
):
    return await service.refresh(data.refresh_token)


@router.post("/logout")
async def logout(
    service: UserServiceDep,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth_scheme),
):
    return await service.logout(token)


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(get_current_user), _: bool = Depends(role_checker)
):
    return current_user
