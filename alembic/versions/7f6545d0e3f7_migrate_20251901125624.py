"""migrate-20251901125624

Revision ID: 7f6545d0e3f7
Revises: a4a76b03643b
Create Date: 2025-01-19 12:56:25.116309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f6545d0e3f7'
down_revision: Union[str, None] = 'a4a76b03643b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('one_time_password', sa.Column('mapper_key', sa.TEXT(), nullable=False))
    op.add_column('one_time_password', sa.Column('mapper_value', sa.TEXT(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('one_time_password', 'mapper_value')
    op.drop_column('one_time_password', 'mapper_key')
    # ### end Alembic commands ###
