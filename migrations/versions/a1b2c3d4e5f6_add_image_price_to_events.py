"""add image_price to events

Revision ID: a1b2c3d4e5f6
Revises: f7d23b1df412
Create Date: 2025-10-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f7d23b1df412'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('events', sa.Column('image_price', sa.Integer(), nullable=True, server_default='2000'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('events', 'image_price')


