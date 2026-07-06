from amqp import basic_message
from amqp import basic_message
from app.schemas.auth import PasswordResetConfirm
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status, BackgroundTasks
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
from app.celery_tasks import send_email
router = APIRouter(prefix="/auth/v1", tags=["Authentication"])
role_checker = RoleChecker(["admin", "user"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(credentials: RegisterUser, bg_tasks : BackgroundTasks, service: UserServiceDep):
    return await service.create(credentials, bg_tasks)


@router.post("/send-mail")
async def send_mail(data: EmailRequest, bg_tasks : BackgroundTasks,):
        recipients = [str(data.email)]
        subject = "Welcome to TaskFlow"
        body = "<h1>Welcome to TaskFlow API!</h1>" 
        try:
            send_email.delay(recipients, subject, body)
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
async def forgot_password(data: PasswordReset, bg_tasks: BackgroundTasks, service: UserServiceDep):
    return await service.reset_password(data.email, bg_tasks)

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
    refresh_token: str | None = Body(default=None, embed=True),
):
    return await service.logout(token, refresh_token)