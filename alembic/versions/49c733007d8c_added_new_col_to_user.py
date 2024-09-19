"""added new col to user

Revision ID: 49c733007d8c
Revises: 358c2a2ad99b
Create Date: 2024-08-23 12:20:33.816627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '49c733007d8c'
down_revision: Union[str, None] = '358c2a2ad99b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
   op.add_column("users", sa.Column("image_url", sa.String, nullable=True))
   
