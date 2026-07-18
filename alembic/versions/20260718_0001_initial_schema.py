"""Initial schema for AI Sales Intelligence Platform.

Revision ID: 20260718_0001
Revises:
Create Date: 2026-07-18
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260718_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables are created by SQLAlchemy metadata on startup for demo simplicity.
    # This revision documents the baseline for Alembic history.
    # Prefer: alembic revision --autogenerate -m "..." in real environments.
    pass


def downgrade() -> None:
    pass
