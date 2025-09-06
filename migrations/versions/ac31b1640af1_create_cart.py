"""create cart

Revision ID: ac31b1640af1
Revises: c9b509603a74
Create Date: 2025-09-01 23:01:33.614710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac31b1640af1'
down_revision: Union[str, Sequence[str], None] = 'c9b509603a74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
