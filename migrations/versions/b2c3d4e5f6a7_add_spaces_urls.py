"""add spaces optimized_url and original_url to images

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-18 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add optimized_url and original_url columns to images table."""
    op.add_column(
        'images',
        sa.Column('optimized_url', sa.String(), nullable=True),
    )
    op.add_column(
        'images',
        sa.Column('original_url', sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Remove optimized_url and original_url columns from images table."""
    op.drop_column('images', 'original_url')
    op.drop_column('images', 'optimized_url')
