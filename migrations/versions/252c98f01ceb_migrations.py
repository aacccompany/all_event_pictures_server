"""migrations

Revision ID: 252c98f01ceb
Revises: 60656a787e25
Create Date: 2025-08-18 14:25:16.509782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '252c98f01ceb'
down_revision: Union[str, Sequence[str], None] = '60656a787e25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
