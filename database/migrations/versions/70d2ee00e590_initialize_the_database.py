"""initialize the database

Revision ID: 70d2ee00e590
Revises: 
Create Date: 2022-10-29 14:37:10.688373

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '70d2ee00e590'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
    op.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    op.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin;"))

    op.create_table('profile',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('USER', 'ADMIN', name='role'), server_default='USER', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index('username_idx', 'profile', ['username'], unique=False, postgresql_using='gin', postgresql_ops={'username': 'gin_trgm_ops'})
    op.create_table('jwt_refresh_token',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('profile_id', postgresql.UUID(), nullable=False),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('invalidated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('previous_token_id', sa.String(), nullable=True),
    sa.Column('valid', sa.Boolean(), server_default='true', nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('profile_id', postgresql.UUID(), nullable=False),
    sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('read', sa.Boolean(), server_default='false', nullable=True),
    sa.Column('visited', sa.Boolean(), server_default='false', nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_created_at'), 'notification', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notification_created_at'), table_name='notification')
    op.drop_table('notification')
    op.drop_table('jwt_refresh_token')
    op.drop_index('username_idx', table_name='profile', postgresql_using='gin', postgresql_ops={'username': 'gin_trgm_ops'})
    op.drop_table('profile')
    # ### end Alembic commands ###
