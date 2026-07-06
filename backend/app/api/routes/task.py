from uuid import UUID

from fastapi import APIRouter, Depends, status, Request
from app.core.limiter import limiter

from app.api.dependencies import RoleChecker, TaskServiceDep, get_current_user
from app.models.user import User
from app.schemas.task import CreateTask, ReadTask, UpdateTask

task_role_checker = Depends(RoleChecker(["admin", "user"]))

router = APIRouter(
    prefix="/api/v1",
    tags=["Tasks"],
    dependencies=[task_role_checker],
)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=ReadTask,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("100/minute")
async def create_task(
    request: Request,
    project_id: UUID,
    data: CreateTask,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.create(user.id, project_id, data)


@router.get("/projects/{project_id}/tasks", response_model=list[ReadTask])
@limiter.limit("100/minute")
async def get_project_tasks(
    request: Request,
    project_id: UUID,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_project_tasks(user.id, project_id)


@router.get("/tasks/{task_id}", response_model=ReadTask)
@limiter.limit("100/minute")
async def get_task(
    request: Request,
    task_id: UUID,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_task(user.id, task_id)


@router.patch("/tasks/{task_id}", response_model=ReadTask)
@limiter.limit("100/minute")
async def update_task(
    request: Request,
    task_id: UUID,
    data: UpdateTask,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.update_task(user.id, task_id, data)


@router.delete("/tasks/{task_id}")
@limiter.limit("100/minute")
async def delete_task(
    request: Request,
    task_id: UUID,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.delete_task(user.id, task_id)
