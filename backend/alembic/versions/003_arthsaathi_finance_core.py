"""Add the ArthSaathi household and small-business finance foundation.

Revision ID: 003_arthsaathi_finance_core
Revises: 002_update_application_table
"""
from alembic import op
import sqlalchemy as sa

revision = "003_arthsaathi_finance_core"
down_revision = "002_update_application_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "financial_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_mode", sa.String(length=20), nullable=False, server_default="household"),
        sa.Column("current_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("preferred_language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", name="uq_financial_profiles_user_id"),
    )
    op.create_index("ix_financial_profiles_id", "financial_profiles", ["id"])
    op.create_index("ix_financial_profiles_user_id", "financial_profiles", ["user_id"])

    op.create_table(
        "financial_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("context_type", sa.String(length=20), nullable=False, server_default="household"),
        sa.Column("entry_type", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("description", sa.String(length=240), nullable=True),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("recurrence_frequency", sa.String(length=20), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_financial_entries_id", "financial_entries", ["id"])
    op.create_index("ix_financial_entries_user_id", "financial_entries", ["user_id"])
    op.create_index("ix_financial_entries_user_date", "financial_entries", ["user_id", "occurred_on"])
    op.create_index("ix_financial_entries_user_context", "financial_entries", ["user_id", "context_type"])

    op.create_table(
        "financial_obligations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_type", sa.String(length=30), nullable=False, server_default="bill"),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("recurrence_frequency", sa.String(length=20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_financial_obligations_id", "financial_obligations", ["id"])
    op.create_index("ix_financial_obligations_user_id", "financial_obligations", ["user_id"])
    op.create_index("ix_financial_obligations_user_due", "financial_obligations", ["user_id", "due_date"])

    op.create_table(
        "business_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("business_name", sa.String(length=160), nullable=False),
        sa.Column("business_type", sa.String(length=80), nullable=True),
        sa.Column("opening_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_business_profiles_id", "business_profiles", ["id"])
    op.create_index("ix_business_profiles_user_id", "business_profiles", ["user_id"])

    op.create_table(
        "business_invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("direction", sa.String(length=12), nullable=False),
        sa.Column("counterparty", sa.String(length=160), nullable=False),
        sa.Column("invoice_number", sa.String(length=80), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("amount_paid", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_business_invoices_id", "business_invoices", ["id"])
    op.create_index("ix_business_invoices_user_id", "business_invoices", ["user_id"])
    op.create_index("ix_business_invoices_business_id", "business_invoices", ["business_id"])
    op.create_index("ix_business_invoices_user_due", "business_invoices", ["user_id", "due_date"])
    op.create_index("ix_business_invoices_business_direction", "business_invoices", ["business_id", "direction"])


def downgrade() -> None:
    op.drop_table("business_invoices")
    op.drop_table("business_profiles")
    op.drop_table("financial_obligations")
    op.drop_table("financial_entries")
    op.drop_table("financial_profiles")
