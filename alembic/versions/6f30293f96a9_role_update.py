"""role_update

Revision ID: 6f30293f96a9
Revises: 49c733007d8c
Create Date: 2024-08-29 21:50:08.621468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6f30293f96a9'
down_revision: Union[str, None] = '49c733007d8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("role_code", sa.Integer, nullable=True))
    op.add_column("user_role", 
                  sa.Column("role_code_list", sa.String, nullable=True))
    op.alter_column('user_role', 
                    'role_name', 
                    new_column_name='role_name_list', 
                    type_=sa.String(255))

