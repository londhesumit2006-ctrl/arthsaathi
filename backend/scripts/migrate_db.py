"""Safely apply Alembic migrations to fresh or pre-Alembic development databases."""
import os
import sys

# Import Alembic before adding backend/ to sys.path: the migration scripts
# directory is named "alembic" and must not shadow the installed package.
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
from app.database import engine  # noqa: E402


LEGACY_COLUMNS = {
    "users": {"id", "email", "hashed_password", "full_name", "role", "created_at", "updated_at"},
    "applications": {"id", "user_id", "applicant_type", "full_name", "age", "phone_number", "address", "requested_amount", "loan_purpose", "alternative_data", "status", "created_at", "updated_at"},
    "credit_scores": {"id", "application_id", "credit_score", "default_probability", "risk_category", "shap_explanations", "model_version", "created_at"},
    "admin_users": {"admin_id", "email", "full_name", "password_hash", "role", "permissions", "is_active", "created_at", "updated_at"},
    "audit_logs": {"id", "admin_id", "action", "resource_type", "resource_id", "old_value", "new_value", "timestamp"},
}
LEGACY_TABLES = set(LEGACY_COLUMNS)


def main() -> None:
    config = Config(os.path.join(backend_dir, "alembic.ini"))
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "alembic_version" not in tables and tables.intersection(LEGACY_TABLES):
        missing = LEGACY_TABLES - tables
        if missing:
            raise RuntimeError(
                "Existing database has a partial legacy schema. Back it up and review it "
                f"before migrating. Missing tables: {', '.join(sorted(missing))}"
            )
        inspector = inspect(engine)
        missing_columns = {
            table: sorted(required - {column["name"] for column in inspector.get_columns(table)})
            for table, required in LEGACY_COLUMNS.items()
        }
        missing_columns = {table: columns for table, columns in missing_columns.items() if columns}
        if missing_columns:
            details = "; ".join(f"{table}: {', '.join(columns)}" for table, columns in missing_columns.items())
            raise RuntimeError(
                "Existing database does not match the expected legacy schema. "
                "No migration was applied. Back up and review manually. Missing columns: " + details
            )
        # The original app created its tables with metadata.create_all() before
        # Alembic was introduced. Stamp only after verifying that full schema.
        command.stamp(config, "002_update_application_table")

    command.upgrade(config, "head")
    print("Database schema is at the latest migration revision.")


if __name__ == "__main__":
    main()
