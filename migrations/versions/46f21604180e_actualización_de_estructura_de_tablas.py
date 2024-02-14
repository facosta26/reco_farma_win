"""Actualización de estructura de tablas

Revision ID: 46f21604180e
Revises: acbf53d057a3
Create Date: 2024-01-09 10:54:12.003542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46f21604180e'
down_revision = 'acbf53d057a3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('doct_mees_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('doct_inst_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_doctors_doct_mees_id', 'medical_especialties', ['doct_mees_id'], ['mees_id'])
        batch_op.create_foreign_key('fk_doctors_doct_inst_id', 'institutions', ['doct_inst_id'], ['inst_id'])

    with op.batch_alter_table('people_prescription', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pepr_phar_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('pepr_dispatched', sa.String(length=1), nullable=True))
        batch_op.add_column(sa.Column('pepr_date_dispatched', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('fk_people_prescription_pepr_phar_id', 'pharmacist', ['pepr_phar_id'], ['phar_id'])

def downgrade():
    with op.batch_alter_table('people_prescription', schema=None) as batch_op:
        batch_op.drop_constraint('fk_people_prescription_pepr_phar_id', type_='foreignkey')
        batch_op.drop_column('pepr_date_dispatched')
        batch_op.drop_column('pepr_dispatched')
        batch_op.drop_column('pepr_phar_id')

    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.drop_constraint('fk_doctors_doct_mees_id', type_='foreignkey')
        batch_op.drop_constraint('fk_doctors_doct_inst_id', type_='foreignkey')
        batch_op.drop_column('doct_inst_id')
        batch_op.drop_column('doct_mees_id')


    # ### end Alembic commands ###
