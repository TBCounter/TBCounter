"""empty message

Revision ID: 761d10e8252d
Revises: c76072f021b4
Create Date: 2022-09-10 14:22:17.045405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '761d10e8252d'
down_revision = 'c76072f021b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chest', schema=None) as batch_op:
        batch_op.add_column(sa.Column('chest_type_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('chest_name_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('player_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_chest_chest_name_id_ideal_chest_name'), 'ideal_chest_name', ['chest_name_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_chest_chest_type_id_ideal_chest_type'), 'ideal_chest_type', ['chest_type_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_chest_player_id_clan_player'), 'clan_player', ['player_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chest', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_chest_player_id_clan_player'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_chest_chest_type_id_ideal_chest_type'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_chest_chest_name_id_ideal_chest_name'), type_='foreignkey')
        batch_op.drop_column('player_id')
        batch_op.drop_column('chest_name_id')
        batch_op.drop_column('chest_type_id')

    # ### end Alembic commands ###