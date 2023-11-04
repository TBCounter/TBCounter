"""empty message

Revision ID: c774827a7701
Revises: 53c2be729810
Create Date: 2022-09-24 16:32:23.750855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c774827a7701'
down_revision = '53c2be729810'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('log_cookie', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('cookieyesID', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('PTBHSSID', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('PTBHSSID')
        batch_op.drop_column('cookieyesID')
        batch_op.drop_column('log_cookie')

    # ### end Alembic commands ###
