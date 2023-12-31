"""empty message

Revision ID: 53c2be729810
Revises: 5055e0faaf9a
Create Date: 2022-09-15 17:49:48.284905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53c2be729810'
down_revision = '5055e0faaf9a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chest_score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('chest_type', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name=op.f('fk_chest_score_account_id_account')),
    sa.ForeignKeyConstraint(['chest_type'], ['ideal_chest_type.id'], name=op.f('fk_chest_score_chest_type_ideal_chest_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_chest_score'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chest_score')
    # ### end Alembic commands ###
