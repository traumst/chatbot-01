"""add hash, allow update

Revision ID: 27de1d703fc2
Revises: f8103e274133
Create Date: 2025-02-15 18:22:51.605393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27de1d703fc2'
down_revision: Union[str, None] = 'f8103e274133'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_query_logs_created_at'), 'query_logs', ['created_at'], unique=False)
    op.add_column('query_logs', sa.Column('hash', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_query_logs_hash'), 'query_logs', ['hash'], unique=False)
    op.add_column('query_logs', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_query_logs_updated_at'), 'query_logs', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_query_logs_created_at'), table_name='query_logs')
    op.drop_index(op.f('ix_query_logs_hash'), table_name='query_logs')
    op.drop_column('query_logs', 'hash')
    op.drop_index(op.f('ix_query_logs_updated_at'), table_name='query_logs')
    op.drop_column('query_logs', 'updated_at')
    # ### end Alembic commands ###
