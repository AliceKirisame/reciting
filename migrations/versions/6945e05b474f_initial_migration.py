"""initial migration

Revision ID: 6945e05b474f
Revises: e8c74c659ba3
Create Date: 2017-04-21 22:32:32.639422

"""

# revision identifiers, used by Alembic.
revision = '6945e05b474f'
down_revision = 'e8c74c659ba3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(length=64), nullable=True))
    op.drop_index('e_mail', table_name='users')
    op.create_unique_constraint(None, 'users', ['email'])
    op.drop_column('users', 'e_mail')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('e_mail', mysql.VARCHAR(length=64), nullable=True))
    op.drop_constraint(None, 'users', type_='unique')
    op.create_index('e_mail', 'users', ['e_mail'], unique=True)
    op.drop_column('users', 'email')
    ### end Alembic commands ###
