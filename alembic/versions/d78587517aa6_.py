"""empty message

Revision ID: d78587517aa6
Revises: 4958951f266b
Create Date: 2022-08-26 14:21:21.174274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd78587517aa6'
down_revision = '4958951f266b'
branch_labels = None
depends_on = None


def upgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('users', schema=None) as batch_op:
    #     batch_op.create_unique_constraint(batch_op.f('uq_users_email'), ['email'])

    # ### end Alembic commands ###


def downgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('users', schema=None) as batch_op:
    #     batch_op.drop_constraint(batch_op.f('uq_users_email'), type_='unique')

    # ### end Alembic commands ###
