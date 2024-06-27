"""a description

Revision ID: 0236c5850fcd
Revises: bf26a3fe9e79
Create Date: 2024-06-27 16:16:46.365833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0236c5850fcd'
down_revision: Union[str, None] = 'bf26a3fe9e79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('file_content_id_fkey', 'file_content', type_='foreignkey')
    op.create_foreign_key(None, 'file_content', 'file', ['id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'file_content', type_='foreignkey')
    op.create_foreign_key('file_content_id_fkey', 'file_content', 'file', ['id'], ['id'])
    # ### end Alembic commands ###
