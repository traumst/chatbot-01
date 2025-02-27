"""base migration

Revision ID: 5e0171a27d6c
Revises: d2b4d596e904
Create Date: 2025-02-26 02:03:24.638785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e0171a27d6c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'ask_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hash', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=True,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_ask_record_hash'),
        'ask_record',
        ['hash'],
        unique=True,
    )
    op.create_index(
        op.f('ix_ask_record_created_at'),
        'ask_record',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_ask_record_updated_at'),
        'ask_record',
        ['updated_at'],
        unique=False,
    )
    op.create_table(
        'chat_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('author', sa.Text(), nullable=False),
        sa.Column('hash', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=True,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_chat_record_chat_id'),
        'chat_record',
        ['chat_id'],
        unique=True,
    )
    op.create_index(
        op.f('ix_chat_record_hash'),
        'chat_record',
        ['hash'],
        unique=True,
    )
    op.create_index(
        op.f('ix_chat_record_created_at'),
        'chat_record',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_chat_record_updated_at'),
        'chat_record',
        ['updated_at'],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(op.f('ix_ask_record_updated_at'), table_name='ask_record')
    op.drop_index(op.f('ix_ask_record_created_at'), table_name='ask_record')
    op.drop_index(op.f('ix_ask_record_hash'), table_name='ask_record')
    op.drop_table('ask_record')
    op.drop_index(op.f('ix_chat_record_chat_id'), table_name='chat_record')
    op.drop_index(op.f('ix_chat_record_updated_at'), table_name='chat_record')
    op.drop_index(op.f('ix_chat_record_created_at'), table_name='chat_record')
    op.drop_index(op.f('ix_chat_record_hash'), table_name='chat_record')
    op.drop_table('chat_record')
