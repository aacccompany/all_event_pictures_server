"""add cart_id to images

Revision ID: c74bba9106df
Revises: f7d23b1df412
Create Date: 2025-09-01 23:04:40.787229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c74bba9106df'
down_revision: Union[str, Sequence[str], None] = 'f7d23b1df412'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "images",
        sa.Column(
            "cart_id",
            sa.Integer(),
            sa.ForeignKey("cart.id", ondelete="CASCADE"),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("images", "cart_id")
