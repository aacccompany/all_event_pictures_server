"""migrations

Revision ID: 7ef447e714ef
Revises: 252c98f01ceb
Create Date: 2025-08-18 14:25:23.771772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ef447e714ef'
down_revision: Union[str, Sequence[str], None] = '252c98f01ceb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
