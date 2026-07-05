from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.task import CreateTask, UpdateTask


class TaskService:
    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)
        self.project_repository = ProjectRepository(session)
        self.user_repository = UserRepository(session)

    async def _get_owned_project(self, user_id: UUID, project_id: UUID):
        project = await self.project_repository.get_one(user_id, project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    async def _get_owned_task(self, user_id: UUID, task_id: UUID) -> Task:
        task = await self.repository.get_one(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        project = await self.project_repository.get_one(user_id, task.project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task

    async def _resolve_assigned_user(
        self, email: str | None
    ) -> tuple[UUID | None, str | None]:
        """
        Resolve an assignee email to (user_id, email).
        Returns (None, None) if no email is given.
        Raises 404 if the email doesn't match an active user.
        """
        if email is None:
            return None, None

        user = await self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

        return user.id, str(user.email)

    async def create(self, user_id: UUID, project_id: UUID, data: CreateTask) -> Task:
        await self._get_owned_project(user_id, project_id)

        assigned_to_id, assigned_to_email = await self._resolve_assigned_user(
            str(data.assigned_to_email) if data.assigned_to_email else None
        )

        task_data = data.model_dump(exclude={"assigned_to_email"})
        task = Task(
            **task_data,
            assigned_to_id=assigned_to_id,
            assigned_to_email=assigned_to_email,
            project_id=project_id,
            created_by_id=user_id,
        )

        try:
            return await self.repository.create(task)
        except IntegrityError as exc:
            await self.repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create task",
            ) from exc

    async def get_project_tasks(self, user_id: UUID, project_id: UUID) -> list[Task]:
        await self._get_owned_project(user_id, project_id)
        return await self.repository.get_project_tasks(project_id)

    async def get_task(self, user_id: UUID, task_id: UUID) -> Task:
        return await self._get_owned_task(user_id, task_id)

    async def update_task(self, user_id: UUID, task_id: UUID, data: UpdateTask) -> Task:
        task = await self._get_owned_task(user_id, task_id)
        update_data = data.model_dump(exclude_unset=True, exclude={"assigned_to_email"})

        if "assigned_to_email" in data.model_fields_set:
            assigned_to_id, assigned_to_email = await self._resolve_assigned_user(
                str(data.assigned_to_email) if data.assigned_to_email else None
            )
            task.assigned_to_id = assigned_to_id
            task.assigned_to_email = assigned_to_email

        for field, value in update_data.items():
            setattr(task, field, value)

        try:
            return await self.repository.update(task)
        except IntegrityError as exc:
            await self.repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update task",
            ) from exc

    async def delete_task(self, user_id: UUID, task_id: UUID) -> dict[str, str]:
        task = await self._get_owned_task(user_id, task_id)

        try:
            await self.repository.delete(task)
        except IntegrityError as exc:
            await self.repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not delete task",
            ) from exc

        return {"message": "Task deleted successfully"}
