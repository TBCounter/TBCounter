"""empty message

Revision ID: 908e20491918
Revises: 50ba70c9dd1e
Create Date: 2023-01-03 13:46:42.438900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '908e20491918'
down_revision = '50ba70c9dd1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chest_score')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chest_score',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('account_id', sa.INTEGER(), nullable=True),
    sa.Column('level', sa.INTEGER(), nullable=True),
    sa.Column('chest_type', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], name='fk_chest_score_account_id_account'),
    sa.ForeignKeyConstraint(['chest_type'], ['ideal_chest_type.id'], name='fk_chest_score_chest_type_ideal_chest_type'),
    sa.PrimaryKeyConstraint('id', name='pk_chest_score')
    )
    # ### end Alembic commands ###
