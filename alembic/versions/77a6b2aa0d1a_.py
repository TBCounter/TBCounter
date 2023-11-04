"""empty message

Revision ID: 77a6b2aa0d1a
Revises: a31b32dd21b0
Create Date: 2022-04-27 15:45:33.297451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77a6b2aa0d1a'
down_revision = 'a31b32dd21b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('report', sa.Column('hash', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('report', 'hash')
    # ### end Alembic commands ###
