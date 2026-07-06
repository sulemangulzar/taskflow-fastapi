from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, Request
from app.core.limiter import limiter

from app.api.dependencies import ProjectServiceDep, RoleChecker, get_current_user
from app.models.user import User
from app.schemas.project import (
    CreateProject,
    PaginatedResponse,
    ReadProject,
    UpdateProject,
)

project_role_checker = Depends(RoleChecker(["admin", "user"]))

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
    dependencies=[project_role_checker],
)


@router.post("", response_model=ReadProject, status_code=status.HTTP_201_CREATED)
@limiter.limit("60/minute")
async def create_project(
    request: Request,
    data: CreateProject,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.create(data, user.id)


@router.get("", response_model=PaginatedResponse[ReadProject])
@limiter.limit("60/minute")
async def get_all_projects(
    request: Request,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
):
    return await service.get_all(user.id, page, size, search)


@router.get("/{project_id}", response_model=ReadProject)
@limiter.limit("60/minute")
async def get_project(
    request: Request,
    project_id: UUID,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_project(user.id, project_id)


@router.patch("/{project_id}", response_model=ReadProject)
@limiter.limit("60/minute")
async def update_project(
    request: Request,
    project_id: UUID,
    data: UpdateProject,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.update_project(user.id, project_id, data)


@router.delete("/{project_id}")
@limiter.limit("60/minute")
async def delete_project(
    request: Request,
    project_id: UUID,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.delete_project(user.id, project_id)
