from uuid import UUID

from fastapi import APIRouter, Depends, status

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
async def create_task(
    project_id: UUID,
    data: CreateTask,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.create(user.id, project_id, data)


@router.get("/projects/{project_id}/tasks", response_model=list[ReadTask])
async def get_project_tasks(
    project_id: UUID,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_project_tasks(user.id, project_id)


@router.get("/tasks/{task_id}", response_model=ReadTask)
async def get_task(
    task_id: UUID,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.get_task(user.id, task_id)


@router.patch("/tasks/{task_id}", response_model=ReadTask)
async def update_task(
    task_id: UUID,
    data: UpdateTask,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.update_task(user.id, task_id, data)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    return await service.delete_task(user.id, task_id)
