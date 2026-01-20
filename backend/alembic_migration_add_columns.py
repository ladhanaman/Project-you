"""Add retry_metadata and duration_minutes columns

Revision ID: add_retry_metadata_duration
Revises: 
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = 'add_retry_metadata_duration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add retry_metadata column to submissions table
    op.add_column('submissions', sa.Column('retry_metadata', JSON, server_default='{}'))
    
    # Add duration_minutes column to test_metadata table
    op.add_column('test_metadata', sa.Column('duration_minutes', sa.Integer(), server_default='30'))


def downgrade():
    # Remove added columns
    op.drop_column('submissions', 'retry_metadata')
    op.drop_column('test_metadata', 'duration_minutes')
