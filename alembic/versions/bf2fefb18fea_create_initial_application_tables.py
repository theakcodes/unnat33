"""create_initial_application_tables

Revision ID: bf2fefb18fea
Revises: 
Create Date: 2026-09-04 23:59:25.780919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf2fefb18fea'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Create ONLY the 5 new application tables."""
    # 1. data_sources
    op.create_table(
        'data_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('record_count', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('metadata_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_sources_id'), 'data_sources', ['id'], unique=False)
    op.create_index(op.f('ix_data_sources_name'), 'data_sources', ['name'], unique=True)

    # 2. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 3. business_profiles
    op.create_table(
        'business_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('registration_type', sa.String(length=100), nullable=True),
        sa.Column('udyam_registration_number', sa.String(length=50), nullable=True),
        sa.Column('enterprise_type', sa.String(length=50), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('nic_code', sa.String(length=20), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=150), nullable=True),
        sa.Column('is_rural', sa.Boolean(), nullable=True),
        sa.Column('annual_turnover', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('investment_in_plant', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_profiles_business_name'), 'business_profiles', ['business_name'], unique=False)
    op.create_index(op.f('ix_business_profiles_id'), 'business_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_business_profiles_sector'), 'business_profiles', ['sector'], unique=False)
    op.create_index(op.f('ix_business_profiles_state'), 'business_profiles', ['state'], unique=False)
    op.create_index(op.f('ix_business_profiles_udyam_registration_number'), 'business_profiles', ['udyam_registration_number'], unique=True)
    op.create_index(op.f('ix_business_profiles_user_id'), 'business_profiles', ['user_id'], unique=False)

    # 4. research_requests
    op.create_table(
        'research_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('business_profile_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('target_sector', sa.String(length=100), nullable=True),
        sa.Column('target_state', sa.String(length=100), nullable=True),
        sa.Column('target_district', sa.String(length=150), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_profile_id'], ['business_profiles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_requests_business_profile_id'), 'research_requests', ['business_profile_id'], unique=False)
    op.create_index(op.f('ix_research_requests_id'), 'research_requests', ['id'], unique=False)
    op.create_index(op.f('ix_research_requests_status'), 'research_requests', ['status'], unique=False)
    op.create_index(op.f('ix_research_requests_target_sector'), 'research_requests', ['target_sector'], unique=False)
    op.create_index(op.f('ix_research_requests_target_state'), 'research_requests', ['target_state'], unique=False)
    op.create_index(op.f('ix_research_requests_user_id'), 'research_requests', ['user_id'], unique=False)

    # 5. research_reports
    op.create_table(
        'research_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('research_request_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('market_analysis', sa.JSON(), nullable=True),
        sa.Column('recommended_schemes', sa.JSON(), nullable=True),
        sa.Column('llm_insights', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['research_request_id'], ['research_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_reports_id'), 'research_reports', ['id'], unique=False)
    op.create_index(op.f('ix_research_reports_research_request_id'), 'research_reports', ['research_request_id'], unique=False)
    op.create_index(op.f('ix_research_reports_status'), 'research_reports', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema: Drop ONLY the 5 new application tables."""
    op.drop_index(op.f('ix_research_reports_status'), table_name='research_reports')
    op.drop_index(op.f('ix_research_reports_research_request_id'), table_name='research_reports')
    op.drop_index(op.f('ix_research_reports_id'), table_name='research_reports')
    op.drop_table('research_reports')

    op.drop_index(op.f('ix_research_requests_user_id'), table_name='research_requests')
    op.drop_index(op.f('ix_research_requests_target_state'), table_name='research_requests')
    op.drop_index(op.f('ix_research_requests_target_sector'), table_name='research_requests')
    op.drop_index(op.f('ix_research_requests_status'), table_name='research_requests')
    op.drop_index(op.f('ix_research_requests_id'), table_name='research_requests')
    op.drop_index(op.f('ix_research_requests_business_profile_id'), table_name='research_requests')
    op.drop_table('research_requests')

    op.drop_index(op.f('ix_business_profiles_user_id'), table_name='business_profiles')
    op.drop_index(op.f('ix_business_profiles_udyam_registration_number'), table_name='business_profiles')
    op.drop_index(op.f('ix_business_profiles_state'), table_name='business_profiles')
    op.drop_index(op.f('ix_business_profiles_sector'), table_name='business_profiles')
    op.drop_index(op.f('ix_business_profiles_id'), table_name='business_profiles')
    op.drop_index(op.f('ix_business_profiles_business_name'), table_name='business_profiles')
    op.drop_table('business_profiles')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_data_sources_name'), table_name='data_sources')
    op.drop_index(op.f('ix_data_sources_id'), table_name='data_sources')
    op.drop_table('data_sources')
