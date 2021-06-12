"""empty message

Revision ID: 429fbfe291d1
Revises: 2d48e8e9835c
Create Date: 2021-02-22 18:55:10.169774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '429fbfe291d1'
down_revision = '2d48e8e9835c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('country', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('language', sa.String(length=2), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'language')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'country')
    # ### end Alembic commands ###
