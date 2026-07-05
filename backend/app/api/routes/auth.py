from app.schemas.auth import PasswordResetConfirm
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    RoleChecker,
    UserServiceDep,
    get_current_user,
    oauth_scheme,
)
from app.mail import create_message, mail
from app.models.user import User
from app.schemas.auth import EmailRequest, RefreshTokenRequest, RegisterUser, TokenResponse, UserRead, PasswordReset

router = APIRouter(prefix="/auth/v1", tags=["Authentication"])
role_checker = RoleChecker(["admin", "user"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(credentials: RegisterUser, service: UserServiceDep):
    return await service.create(credentials)


@router.post("/send-mail")
async def send_mail(data: EmailRequest):
    message = create_message(
        recipients=[str(data.email)],
        subject="Welcome to TaskFlow",
        body="<h1>Welcome to TaskFlow API!</h1>"
    )
    try:
        await mail.send_message(message)
        return {"message": "Email sent to Mailtrap Sandbox"}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Email failed: {exc}",
        )

@router.get("/verify/{token}")
async def verify_email(token: str, service: UserServiceDep):
    return await service.verify_email(token)

@router.post("/forgot-password")
async def forgot_password(data: PasswordReset, service: UserServiceDep):
    return await service.reset_password(data.email)

@router.post("/reset-password/{token}")
async def reset_password_confirm(token: str, new_credentials: PasswordResetConfirm, service: UserServiceDep):
    return await service.reset_password_confirm(token, new_credentials)


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




@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(get_current_user), _: bool = Depends(role_checker)
):
    try:
        return current_user
    except Exception as e:
        raise 

@router.post("/logout")
async def logout(
    service: UserServiceDep,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth_scheme),
):
    return await service.logout(token)