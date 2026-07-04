from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.projects import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_all(
        self, user_id: UUID, page: int, size: int, search: str | None
    ) -> tuple[list[Project], int]:
        offset = (page - 1) * size
        conditions = [Project.owner_id == user_id]

        if search:
            conditions.append(Project.name.ilike(f"%{search}%"))  # type: ignore[attr-defined]

        total_result = await self.session.execute(
            select(func.count()).select_from(Project).where(*conditions)
        )
        total = total_result.scalar_one()

        result = await self.session.execute(
            select(Project).where(*conditions).offset(offset).limit(size)
        )
        projects = list(result.scalars().all())

        return projects, total

    async def get_one(self, user_id: UUID, project_id: UUID) -> Project | None:
        result = await self.session.execute(
            select(Project).where(
                Project.owner_id == user_id,
                Project.id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
