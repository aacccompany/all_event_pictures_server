"""fix heads

Revision ID: 67f7b0e4f4f0
Revises: a1b2c3d4e5f6, dc9e26991a92
Create Date: 2026-01-06 22:25:14.457397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67f7b0e4f4f0'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'dc9e26991a92')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
