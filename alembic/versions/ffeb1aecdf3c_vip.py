"""vip

Revision ID: ffeb1aecdf3c
Revises: ad70f8ab04e2
Create Date: 2023-07-11 22:35:55.709183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffeb1aecdf3c'
down_revision = 'ad70f8ab04e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('vip', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account', 'vip')
    # ### end Alembic commands ###