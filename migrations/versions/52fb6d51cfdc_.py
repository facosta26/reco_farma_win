"""empty message

Revision ID: 52fb6d51cfdc
Revises: dc14f0bbacbe
Create Date: 2024-01-23 15:07:51.742573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52fb6d51cfdc'
down_revision = 'dc14f0bbacbe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('people_prescription_details', schema=None) as batch_op:
        batch_op.add_column(sa.Column('prde_paty_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('prde_quantity', sa.Integer(), nullable=False))
        batch_op.create_foreign_key("fk_prde_paty_id", 'parcel_type', ['prde_paty_id'], ['paty_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('people_prescription_details', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('prde_quantity')
        batch_op.drop_column('prde_paty_id')

    # ### end Alembic commands ###
