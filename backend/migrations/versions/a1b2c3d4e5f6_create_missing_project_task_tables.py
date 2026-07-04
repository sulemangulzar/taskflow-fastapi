"""create missing project and task tables

Revision ID: a1b2c3d4e5f6
Revises: f0e9bc0c67ce
Create Date: 2026-07-04 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f0e9bc0c67ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            owner_id UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_projects_owner_id
        ON projects (owner_id)
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id UUID PRIMARY KEY,
            title VARCHAR NOT NULL,
            description VARCHAR NULL,
            status VARCHAR NOT NULL,
            priority VARCHAR NOT NULL,
            project_id UUID NOT NULL REFERENCES projects(id),
            created_by_id UUID NOT NULL REFERENCES users(id),
            assigned_to_id UUID NULL REFERENCES users(id),
            due_date TIMESTAMP NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_tasks_project_id
        ON tasks (project_id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_tasks_created_by_id
        ON tasks (created_by_id)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_tasks_created_by_id")
    op.execute("DROP INDEX IF EXISTS ix_tasks_project_id")
    op.execute("DROP TABLE IF EXISTS tasks")
    op.execute("DROP INDEX IF EXISTS ix_projects_owner_id")
    op.execute("DROP TABLE IF EXISTS projects")
