"""empty message

Revision ID: 7866feca65af
Revises: 12717b0032c3
Create Date: 2020-05-21 17:38:12.237755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7866feca65af'
down_revision = '12717b0032c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('datatimeevent_ibfk_2', 'datatimeevent', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('datatimeevent_ibfk_2', 'datatimeevent', 'patients', ['subject_id'], ['subject_id'])
    # ### end Alembic commands ###
