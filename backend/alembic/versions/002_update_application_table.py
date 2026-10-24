"""Compatibility revision: application status and updated_at are in baseline.

Revision ID: 002_update_application_table
Revises: 001_create_admin_tables
"""
revision = "002_update_application_table"
down_revision = "001_create_admin_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Kept to preserve the repository's published revision chain. Fresh baseline
    # installs already contain both columns; existing development databases can
    # be stamped at this revision after their schema is verified.
    pass


def downgrade() -> None:
    pass
