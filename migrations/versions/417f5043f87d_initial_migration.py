"""Initial migration.

Revision ID: 417f5043f87d
Revises: 44d55a409684
Create Date: 2023-02-17 14:45:24.861510

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '417f5043f87d'
down_revision = '44d55a409684'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_post', schema=None) as batch_op:
        batch_op.alter_column('longitude',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('latitude',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('location',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_post', schema=None) as batch_op:
        batch_op.alter_column('location',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
        batch_op.alter_column('latitude',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('longitude',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)

    # ### end Alembic commands ###