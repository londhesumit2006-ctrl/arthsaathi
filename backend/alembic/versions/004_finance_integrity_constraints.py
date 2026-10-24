"""Add database-level integrity checks to ArthSaathi finance records.

Revision ID: 004_finance_integrity
Revises: 003_arthsaathi_finance_core
"""
from alembic import op
import sqlalchemy as sa

revision = "004_finance_integrity"
down_revision = "003_arthsaathi_finance_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Batch operations support SQLite development databases as well as PostgreSQL.
    constraints = {
        "financial_profiles": [
            ("ck_financial_profiles_account_mode", "account_mode IN ('household', 'business', 'both')"),
            ("ck_financial_profiles_current_balance_nonnegative", "current_balance >= 0"),
        ],
        "financial_entries": [
            ("ck_financial_entries_context_type", "context_type IN ('household', 'business')"),
            ("ck_financial_entries_entry_type", "entry_type IN ('income', 'expense')"),
            ("ck_financial_entries_amount_positive", "amount > 0"),
        ],
        "financial_obligations": [
            ("ck_financial_obligations_amount_positive", "amount > 0"),
            ("ck_financial_obligations_status", "status IN ('pending', 'paid', 'cancelled')"),
        ],
        "business_profiles": [
            ("ck_business_profiles_opening_balance_nonnegative", "opening_balance >= 0"),
        ],
        "business_invoices": [
            ("ck_business_invoices_direction", "direction IN ('receivable', 'payable')"),
            ("ck_business_invoices_total_positive", "total_amount > 0"),
            ("ck_business_invoices_amount_paid_range", "amount_paid >= 0 AND amount_paid <= total_amount"),
            ("ck_business_invoices_status", "status IN ('open', 'partial', 'paid', 'cancelled')"),
        ],
    }
    for table_name, table_constraints in constraints.items():
        with op.batch_alter_table(table_name) as batch_op:
            for name, expression in table_constraints:
                batch_op.create_check_constraint(name, expression)


def downgrade() -> None:
    constraint_names = {
        "financial_profiles": ["ck_financial_profiles_account_mode", "ck_financial_profiles_current_balance_nonnegative"],
        "financial_entries": ["ck_financial_entries_context_type", "ck_financial_entries_entry_type", "ck_financial_entries_amount_positive"],
        "financial_obligations": ["ck_financial_obligations_amount_positive", "ck_financial_obligations_status"],
        "business_profiles": ["ck_business_profiles_opening_balance_nonnegative"],
        "business_invoices": ["ck_business_invoices_direction", "ck_business_invoices_total_positive", "ck_business_invoices_amount_paid_range", "ck_business_invoices_status"],
    }
    for table_name, names in constraint_names.items():
        with op.batch_alter_table(table_name) as batch_op:
            for name in names:
                batch_op.drop_constraint(name, type_="check")
