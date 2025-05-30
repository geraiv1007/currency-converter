"""'initial'

Revision ID: 0e5dc120ee8a
Revises: 
Create Date: 2025-04-14 20:59:56.471251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e5dc120ee8a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('username', sa.Text(), nullable=True),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username'),
    schema='currency_converter'
    )
    op.create_table('jwt_tokens',
    sa.Column('token_id', sa.Text(), nullable=False),
    sa.Column('token_type', sa.String(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('revoked', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['email'], ['currency_converter.users.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('token_id'),
    schema='currency_converter'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jwt_tokens', schema='currency_converter')
    op.drop_table('users', schema='currency_converter')
    # ### end Alembic commands ###
