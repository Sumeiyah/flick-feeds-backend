"""Add owned_clubs relationship to User and owner relationship to Club

Revision ID: 4a1a6d9ceabc
Revises: 4389838f2f1b
Create Date: 2024-11-30 16:03:38.920339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a1a6d9ceabc'
down_revision = '4389838f2f1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clubs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ImageURL', sa.String(length=255), nullable=True))
        batch_op.alter_column('Genre',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clubs', schema=None) as batch_op:
        batch_op.alter_column('Genre',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
        batch_op.drop_column('ImageURL')

    # ### end Alembic commands ###