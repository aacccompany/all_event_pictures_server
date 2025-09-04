"""create cart_images table

Revision ID: e01368550c83
Revises: 8f31e1dca8e1
Create Date: 2025-09-04 21:27:08.198883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e01368550c83'
down_revision: Union[str, Sequence[str], None] = '8f31e1dca8e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "cart_images",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("cart_id", sa.Integer, sa.ForeignKey("cart.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_id", sa.Integer, sa.ForeignKey("images.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("cart_id", "image_id", name="uq_cart_image")  # ป้องกัน duplicate
    )


def downgrade() -> None:
    op.drop_table("cart_images")

