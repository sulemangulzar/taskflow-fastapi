from fastapi import APIRouter, Depends, status

from app.api.dependencies import ProjectServiceDep, get_current_user
from app.models.user import User
from app.schemas.project import CreateProject, ReadProject

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


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
