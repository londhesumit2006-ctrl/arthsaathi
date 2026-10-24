# Start here — ArthSaathi

## 1. Open the project

Extract this ZIP. Open the `hackohire` folder in VS Code.

## 2. Start the backend

1. Install Python 3.10+ and PostgreSQL 14+ (or Docker Desktop).
2. Copy `backend/.env.example` to `backend/.env`.
3. Set `DATABASE_URL` and generate a unique `SECRET_KEY`.
4. In a terminal:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/migrate_db.py
uvicorn app.main:app --reload --port 8000
```

For macOS/Linux, activate with `source .venv/bin/activate`.

## 3. Start the website

Open a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Then open **http://localhost:3000**.

## 4. Create your first account

Use **Get started** on the home page. After registration, the site opens the ArthSaathi workspace.

## 5. Main areas

Overview · Household finances · Small business · Debt & loan planner · Savings planner · Financial safety · Schemes & support · Document helper · Money guide · Monthly report · Settings.

## Important before real users

This is a development MVP, not a production financial service. Review `README.md` and `docs/ARTHSAATHI_WEBSITE.md`. The savings planner is browser-local; scheme discovery uses official links; the document helper is a basic local keyword scan. WhatsApp, bank integrations and AI chat are not connected. Complete security review and authenticated cross-user API tests before any public pilot.
