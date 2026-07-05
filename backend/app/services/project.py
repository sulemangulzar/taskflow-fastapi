from app.core.utils import create_url_safe_token
from app.core.config import settings
from math import ceil
from uuid import UUID

from app.errors import InputValidationError, ProjectNotFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import CreateProject, UpdateProject


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.repository = ProjectRepository(session)

    async def create(self, data: CreateProject, owner_id: UUID) -> Project:
        project = Project(
            **data.model_dump(),
            owner_id=owner_id,
        )

        try:
            return await self.repository.create(project)
        except IntegrityError as exc:
            await self.repository.rollback()
            raise InputValidationError("Could not create project") from exc

    async def get_all(
        self, user_id: UUID, page: int, size: int, search: str | None
    ) -> dict:
        projects, total = await self.repository.get_all(user_id, page, size, search)

        return {
            "items": projects,
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total else 0,
        }

    async def get_project(self, user_id: UUID, project_id: UUID) -> Project:
        project = await self.repository.get_one(user_id, project_id)
        if project is None:
            raise ProjectNotFound()
        return project

    async def update_project(
        self, user_id: UUID, project_id: UUID, data: UpdateProject
    ) -> Project:
        project = await self.get_project(user_id, project_id)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(project, field, value)

        try:
            return await self.repository.update(project)
        except IntegrityError as exc:
            await self.repository.rollback()
            raise InputValidationError("Could not update project") from exc

    async def delete_project(self, user_id: UUID, project_id: UUID) -> dict[str, str]:
        project = await self.get_project(user_id, project_id)

        try:
            await self.repository.delete(project)
        except IntegrityError as exc:
            print(exc)
            await self.repository.rollback()
            raise InputValidationError("Could not delete project") from exc

        return {"message": "Project deleted successfully"}
