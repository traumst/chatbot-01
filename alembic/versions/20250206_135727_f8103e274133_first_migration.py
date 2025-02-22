"""first migration

Revision ID: f8103e274133
Revises: 
Create Date: 2025-02-06 13:57:27.363758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8103e274133'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'query_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('query_text', sa.Text, nullable=False),
        sa.Column('response_text', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('query_logs')
