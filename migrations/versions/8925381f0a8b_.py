"""empty message

Revision ID: 8925381f0a8b
Revises: c2127e2646d7
Create Date: 2020-05-11 22:20:00.173136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8925381f0a8b'
down_revision = 'c2127e2646d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('correct', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'correct')
    # ### end Alembic commands ###
