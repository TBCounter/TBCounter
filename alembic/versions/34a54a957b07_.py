"""empty message

Revision ID: 34a54a957b07
Revises: d78587517aa6
Create Date: 2022-08-31 19:48:14.030283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34a54a957b07'
down_revision = 'd78587517aa6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clan_player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hash', sa.String(length=64), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('path', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name=op.f('fk_clan_player_account_id_account')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_clan_player'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('clan_player')
    # ### end Alembic commands ###
