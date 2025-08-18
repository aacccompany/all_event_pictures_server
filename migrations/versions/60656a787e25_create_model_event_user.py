"""create model event_user

Revision ID: 60656a787e25
Revises: bbcb0991451f
Create Date: 2025-08-18 13:57:45.240251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60656a787e25'
down_revision: Union[str, Sequence[str], None] = 'bbcb0991451f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
