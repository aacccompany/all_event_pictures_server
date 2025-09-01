"""create cart

Revision ID: c9b509603a74
Revises: f5d41b33b19e
Create Date: 2025-09-01 22:58:02.899111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9b509603a74'
down_revision: Union[str, Sequence[str], None] = 'f5d41b33b19e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
