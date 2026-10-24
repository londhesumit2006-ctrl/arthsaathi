# ArthSaathi

**Your money. Your decisions. A little more clarity.**

ArthSaathi is an early-stage financial companion for Indian households, workers, self-employed people and small businesses. The current MVP focuses on household money tracking, small-business cash records, upcoming payments, cash-flow planning, loan-cost calculations, financial safety guidance and plain-language financial education.

> This software is a planning and record-keeping tool. It is not a bank, lender, credit bureau, investment adviser, audited accounting system or legal adviser. Forecasts are estimates based on information users enter.

## Product areas in the current website

- **Overview:** available balance, recorded monthly income and expenses, 30-day projected balance, upcoming commitments and recent activity.
- **Household finances:** record actual income and expenses; add rent, EMI, school-fee and bill commitments; mark commitments as paid.
- **Small business:** create business profiles, record sales and expenses, track customer receivables and supplier payables, update invoice payments.
- **Debt & loan planner:** estimate EMI, total repayment, interest and a simple monthly budget indicator.
- **Savings planner:** calculate progress toward an emergency fund or savings goal. The current plan is stored locally in the user's browser.
- **Financial safety:** immediate cyber-fraud response steps and official reporting links.
- **Schemes & support:** links to selected official government portals. ArthSaathi does not determine or guarantee eligibility.
- **Document helper:** local keyword scan for common loan terms in text pasted by the user. It does not upload, authenticate or legally interpret documents.
- **Money guide:** plain-language educational answers to common financial questions.
- **Monthly report:** recorded income/expense summary and CSV export.
- **Settings:** household/business mode, starting balance and language preference.

The public landing page, login, registration and authenticated finance workspace are part of the same website. The interface is responsive for desktop and mobile browsers.

## Stack

- Frontend: React 18, TypeScript, Vite, React Router
- Backend: FastAPI, Python, SQLAlchemy
- Database: PostgreSQL (SQLite can be used for local tests)
- Migrations: Alembic

## Run locally

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or Docker Desktop)

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env`. Set a unique `SECRET_KEY` and configure `DATABASE_URL` for your local PostgreSQL database. Then run:

```bash
python scripts/migrate_db.py
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Website: http://localhost:3000

Set `VITE_API_URL` if your API is not at `http://localhost:8000`. The Vite dev server proxies `/api` to the backend as configured in `vite.config.ts`.

### 4. Docker Compose

From the project root:

```bash
docker compose up --build
```

Website: http://localhost:3000  
API docs: http://localhost:8000/docs

Change all development credentials and secrets before using a shared or production environment. Back up any existing database before running migrations.

## Existing project migration notes

- Existing authentication and legacy credit-scoring routes are retained for compatibility.
- New registrations and logins open the ArthSaathi finance workspace at `/money`.
- Finance schema migrations are documented in `docs/DATABASE_MIGRATIONS.md`.
- Do not describe the legacy experimental credit score as an official CIBIL or bureau score. Its original training data is not representative of Indian borrower outcomes.

## Current limitations — read before pilot use

- Core household and business entries, obligations, business profiles and invoices use the FastAPI backend.
- The savings planner currently stores its plan in the current browser only; it is not synced across devices.
- The document helper is a browser-side keyword scan for pasted text, not OCR or an AI/legal review.
- Scheme discovery is a curated set of official links, not a live eligibility engine.
- Financial safety guidance is informational; active fraud should be reported immediately through the bank and official channels.
- WhatsApp automation, bank/UPI integrations, Account Aggregator access, OCR, AI chat, recurring transaction generation and production-grade notifications are not connected in this release.
- Complete authenticated API ownership tests, security review, production deployment review and user pilot validation are required before public launch.

## Team workflow

See:
- `docs/ARTHSAATHI_MVP_PLAN.md`
- `docs/DATABASE_MIGRATIONS.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/ARTHSAATHI_WEBSITE.md`

Suggested team split for 3–4 contributors:
1. Backend, database and access-control tests
2. Frontend and responsive experience
3. Financial calculations, QA and test scenarios
4. User research, onboarding language and pilot operations

All financial calculations and AI-assisted code changes must be reviewed and tested before release.
