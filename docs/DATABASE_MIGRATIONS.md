# ArthSaathi database schema and migrations

## Current schema additions

### `financial_profiles`

One row per user. Stores `account_mode` (`household`, `business`, `both`), manually entered current available balance, currency and preferred language.

### `financial_entries`

One row per received income or paid expense. `context_type` separates household and business activity. Amounts use `NUMERIC(14,2)`, not floating-point storage. Future-dated income can represent expected income; future expenses belong in obligations to avoid double counting.

### `financial_obligations`

Upcoming or overdue household commitments such as bills, rent, school fees and EMIs. `status` is `pending`, `paid` or `cancelled`. A pending overdue obligation remains part of the pressure calculation.

### `business_profiles`

A user can maintain one or more small-business profiles. Business records remain scoped to the owner.

### `business_invoices`

Tracks `receivable` (customer owes the business) and `payable` (business owes supplier), with total and paid amounts. Forecasts use only the unpaid remainder. Partial payment is supported.

## Relationships

```text
users
 ├── financial_profiles (1:1)
 ├── financial_entries (1:N)
 ├── financial_obligations (1:N)
 └── business_profiles (1:N)
       └── business_invoices (1:N)
```

`business_invoices` also carries `user_id` to make owner filtering explicit. The API checks that the selected `business_id` belongs to the signed-in user before creating an invoice.

## Migration revisions

| Revision | Purpose |
|---|---|
| `001_create_admin_tables` | Normalised original schema baseline for a fresh database: users, applications, credit_scores, admin_users, audit_logs |
| `002_update_application_table` | Compatibility revision; status and updated_at are already part of the baseline |
| `003_arthsaathi_finance_core` | Adds five ArthSaathi finance tables and their indexes/foreign keys |
| `004_finance_integrity_constraints` | Adds database-level checks for allowed modes, types, statuses and valid amounts |

The first two revisions were normalised in this pre-launch repository to allow a clean installation. Revision 004 adds integrity checks; do not rewrite migrations after they have been applied in a shared or production database. If another developer's database has the original tables but no `alembic_version`, `scripts/migrate_db.py` verifies the legacy table set, stamps it at revision 002, then applies revisions 003 and 004. Back up first. A partial schema deliberately stops for manual review.

## Commands

Run the migration helper from the repository root (or from `backend/`). It handles a fresh database and a verified legacy development database:

```bash
python backend/scripts/migrate_db.py
```

To inspect or apply a migration directly from the repository root:

```bash
alembic -c backend/alembic.ini current
alembic -c backend/alembic.ini history
alembic -c backend/alembic.ini upgrade head
```

For a fresh disposable SQLite migration check:

```bash
DATABASE_URL=sqlite:////tmp/arthsaathi-check.db alembic -c backend/alembic.ini upgrade head
```

## Cash-flow calculation semantics

For the next 30 days:

```text
projected balance = current available balance
                  + future expected income entries
                  - pending obligations due on or before day 30
                  + unpaid receivables due on or before day 30
                  - unpaid payables due on or before day 30
```

Overdue pending obligations and overdue open/partial invoices are included because they still need attention. Historical entries are not added to current balance: the user-entered current balance is the starting point. Do not record an unpaid invoice as received income. Do not add the same future outgoing amount both as a future expense entry and as an obligation.

Household and business calculations are requested separately (`context_type=household` or `context_type=business`). Household calculations use the household available balance and household obligations only. Business calculations use business opening balances, future expected business income and unpaid invoices only. This prevents business receivables from being treated as household cash.

The indicator thresholds are intentionally simple and should be calibrated through pilot feedback; they are not a financial-risk score. The output must always disclose that the estimate is based on user-entered data.

## Before production

- Add automated migration tests against PostgreSQL, not SQLite alone.
- Add PostgreSQL migration tests and keep database constraints in sync with SQLAlchemy models.
- Add pagination and query limits to all list endpoints.
- Add consent records, audit events for sensitive access, export/deletion workflows and retention policy.
- Use database backups and test restore procedures.
- Move secrets out of compose defaults and rotate any previously shared development credentials.
