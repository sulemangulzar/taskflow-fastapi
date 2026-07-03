from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import CreateProject


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
            raise HTTPException(
                status_code=400,
                detail="Could not create project",
            ) from exc

    async def get_all(self, user_id: UUID):
        return await self.repository.get_all(user_id)
