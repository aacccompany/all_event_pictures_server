"""create cart

Revision ID: f5d41b33b19e
Revises: 1e2da4c9d201
Create Date: 2025-09-01 22:51:23.648094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5d41b33b19e'
down_revision: Union[str, Sequence[str], None] = '1e2da4c9d201'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
