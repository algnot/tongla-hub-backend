"""migrate-20251701210020

Revision ID: 77464fadaf31
Revises: 
Create Date: 2025-01-17 21:00:20.616945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77464fadaf31'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARBINARY(length=200), nullable=False),
    sa.Column('email', sa.VARBINARY(length=200), nullable=False),
    sa.Column('hashed_password', sa.VARBINARY(length=200), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('role', sa.Enum('USER', 'ADMIN', name='roletype'), nullable=False),
    sa.Column('image_url', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('user_tokens',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('ACCESS', 'REFRESH', 'RESET_PASSWORD', name='tokentype'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('revoked', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_tokens')
    op.drop_table('users')
    # ### end Alembic commands ###
