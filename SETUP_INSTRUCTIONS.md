# ArthSaathi — Local setup guide

This repository is transitioning from the HackOHire credit-scoring prototype to ArthSaathi, an everyday financial companion. For the first release, use the household and small-business finance workspace at `/money`. The old credit application screens are retained only for transition and should not be used as an official credit score or lending decision.

## 1. Prerequisites

- Python 3.10 or newer
- Node.js 20 or newer and npm
- PostgreSQL 14+ (or SQLite for local experiments)

## 2. Configure the backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
```

Set `DATABASE_URL` to your local database and replace `SECRET_KEY` with a long random value. Never commit `.env` or share it in screenshots.

Run the database migrations and start FastAPI:

```bash
python scripts/migrate_db.py
uvicorn app.main:app --reload
```

API documentation: http://localhost:8000/docs

## 3. Configure the frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Register or sign in; the app opens the ArthSaathi workspace at http://localhost:3000/money.

## 4. Docker Compose

From the repository root, set a secure `SECRET_KEY` in your shell or local environment file, then run:

```bash
docker compose up --build
```

Local services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## 5. Run tests

```bash
cd backend
PYTHONPATH=. pytest -q
```

For a clean SQLite migration check, from the repository root:

```bash
DATABASE_URL=sqlite:////tmp/arthsaathi-check.db alembic -c backend/alembic.ini upgrade head
```

## 6. MVP workflow

1. Set the account mode to household, business or both.
2. Enter the current available household balance.
3. Record money already received or paid.
4. Add future income only when it is reasonably expected.
5. Add upcoming household bills and EMIs as obligations.
6. In business mode, create a business and record customer receivables or supplier payables.
7. Review the separate 30-day household or business estimate.

All estimates depend on user-entered data. Manual entries are not independently verified. Future expenses should be recorded as obligations, not as paid expenses. Do not enter banking passwords, UPI PINs, card PINs or OTPs.

## 7. Development ownership

See `docs/ARTHSAATHI_MVP_PLAN.md` for the four-contributor assignment and six-week schedule. See `docs/DATABASE_MIGRATIONS.md` before changing the database schema.
