"""Updated task - assigned_to_email already included in initial migration

Revision ID: 479577c94cb8
Revises: 186edb507627
Create Date: 2026-07-04 15:36:12.095564

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "479577c94cb8"
down_revision: Union[str, Sequence[str], None] = "186edb507627"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    NOTE: assigned_to_email was originally added here as nullable=False (a bug).
    It is now included in the initial migration (186edb507627) as nullable=True.
    This migration is kept only to preserve the revision chain.

    If applying to an existing DB that ran the old initial migration WITHOUT
    assigned_to_email, uncomment the block below:

    op.add_column(
        "tasks",
        sa.Column("assigned_to_email", sa.String(length=320), nullable=True),
    )
    """
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
