"""empty message

Revision ID: abf2a4a1ab6a
Revises: 11cf8f67e61a
Create Date: 2020-05-06 21:34:02.887773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abf2a4a1ab6a'
down_revision = '11cf8f67e61a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'cars', 'user', ['username'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'cars', type_='foreignkey')
    # ### end Alembic commands ###
