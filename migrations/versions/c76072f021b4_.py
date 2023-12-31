"""empty message

Revision ID: c76072f021b4
Revises: 28cdf72ae455
Create Date: 2022-09-07 20:44:38.568718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c76072f021b4'
down_revision = '28cdf72ae455'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clan_player', schema=None) as batch_op:
        batch_op.add_column(sa.Column('level', sa.Integer(), nullable=True))
        batch_op.drop_column('league')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clan_player', schema=None) as batch_op:
        batch_op.add_column(sa.Column('league', sa.INTEGER(), nullable=True))
        batch_op.drop_column('level')

    # ### end Alembic commands ###
