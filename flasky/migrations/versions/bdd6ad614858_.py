"""empty message

Revision ID: bdd6ad614858
Revises: 00520ea1f8b6
Create Date: 2019-04-22 21:27:24.444804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdd6ad614858'
down_revision = '00520ea1f8b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bikes', sa.Column('rented_time', sa.Integer(), nullable=True))
    op.add_column('bikes', sa.Column('total_charge', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bikes', 'total_charge')
    op.drop_column('bikes', 'rented_time')
    # ### end Alembic commands ###
