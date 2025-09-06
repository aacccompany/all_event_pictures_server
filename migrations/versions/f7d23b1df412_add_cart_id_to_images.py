"""add cart_id to images

Revision ID: f7d23b1df412
Revises: ac31b1640af1
Create Date: 2025-09-01 23:03:04.005999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7d23b1df412'
down_revision: Union[str, Sequence[str], None] = 'ac31b1640af1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
