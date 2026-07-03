from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import ProjectServiceDep, RoleChecker, get_current_user
from app.models.user import User
from app.schemas.project import CreateProject, ReadProject, UpdateProject

project_role_checker = Depends(RoleChecker(["admin", "user"]))

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
    dependencies=[project_role_checker],
)


@router.post("", response_model=ReadProject, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProject,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.create(data, user.id)


@router.get("", response_model=list[ReadProject])
async def get_all_projects(
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_all(user.id)


@router.get("/{project_id}", response_model=ReadProject)
async def get_project(
    project_id: UUID,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_project(user.id, project_id)


@router.patch("/{project_id}", response_model=ReadProject)
async def update_project(
    project_id: UUID,
    data: UpdateProject,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.update_project(user.id, project_id, data)


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
    service: ProjectServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.delete_project(user.id, project_id)
