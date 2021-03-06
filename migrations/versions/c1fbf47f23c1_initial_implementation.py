"""Initial implementation

Revision ID: c1fbf47f23c1
Revises: 
Create Date: 2021-01-04 10:22:37.119805

"""
from alembic import op
from app import models
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = 'c1fbf47f23c1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('description', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('flask_dance_oauth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('token', sqlalchemy_utils.types.json.JSONType(), nullable=False),
    sa.Column('provider_user_id', sa.String(length=256), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('issuer', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider', 'provider_user_id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sla',
    #sa.Column('id', app.utils.sqlalchemy_helpers.GUID(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('customer', sa.String(length=64), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=False),
    sa.Column('provider', sa.String(length=64), nullable=False),
    sa.Column('vcpu_cores', sa.Integer(), nullable=True),
    sa.Column('ram_gb', sa.Integer(), nullable=True),
    sa.Column('public_ips', sa.Integer(), nullable=True),
    sa.Column('storage_gb', sa.Integer(), nullable=True),
    sa.Column('num_instances', sa.Integer(), nullable=True),
    #sa.Column('status', app.utils.sqlalchemy_helpers.IntEnum(), nullable=True),
    sa.Column('status', models.IntEnum(models.SlaStatusTypes), nullable=True),
    sa.ForeignKeyConstraint(['customer'], ['group.name'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type', 'customer')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sla')
    op.drop_table('roles')
    op.drop_table('flask_dance_oauth')
    op.drop_table('user')
    op.drop_table('group')
    # ### end Alembic commands ###
