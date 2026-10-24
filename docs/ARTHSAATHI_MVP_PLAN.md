# ArthSaathi — MVP execution plan

## Product boundary for Version 1

**User groups:** households, salaried and irregular-income workers, self-employed people, and micro/small businesses.

**First problem:** make money in, money out, upcoming obligations and unpaid business dues visible in one simple place.

**Channels:** responsive web first. WhatsApp is a later integration after the workflow, consent, security and API costs are understood.

**Pricing:** free for individuals during the pilot. No ads based on financial data, lead selling or loan pushing.

### Included in MVP

1. Registration/login using the existing account system.
2. Household, business or combined account mode.
3. User-entered current balance.
4. Income and expense ledger.
5. Upcoming household obligations (rent, bills, school fees, EMIs and other payments).
6. Business profiles, sales/expenses, customer receivables and supplier payables.
7. 30-day cash position estimate with clear explanation and data caveat.
8. Monthly report and CSV export (next sprint).

### Explicitly out of scope

- New credit score or loan approval model.
- Lending marketplace, payments, wallet or money movement.
- Bank/UPI credentials or automated account scraping.
- Account Aggregator integration before consent, partner and legal readiness.
- Investment/insurance recommendations.
- Automated WhatsApp messaging before a privacy and operational review.
- AI-generated financial recommendations without verified data and testable rules.

## Team ownership for 3–4 contributors

| Role | Primary ownership | Deliverables | Review responsibility |
|---|---|---|---|
| Contributor A — Backend/data | FastAPI, SQLAlchemy models, Alembic, authentication integration, ownership checks | API routes, schemas, migrations, API tests | Reviews all data access and migration PRs |
| Contributor B — Frontend/product | React pages, responsive layouts, onboarding, forms, dashboard | `/money` experience, accessible forms, empty/error states | Reviews UI consistency and user testing feedback |
| Contributor C — Finance logic/QA | Cash-flow rules, debt/bill semantics, business ledger rules, test scenarios | Calculation specifications, edge-case tests, sample datasets | Independently verifies arithmetic and warnings |
| Contributor D — Research/operations (if available) | Interviews, Hindi wording, usability tests, privacy checklist, pilot support | Interview notes, issue triage, help content | Checks that copy is understandable and not misleading |

If only three people are available, Contributor C also owns user research and QA. Every change should have one author and one reviewer; AI-generated code must be read and tested by a human before merge.

## Working agreement

- `main` is always runnable; use short-lived branches: `feat/finance-profile`, `feat/household-ledger`, etc.
- Pull requests should be small and include screenshots/API examples plus tests.
- Never commit `.env`, credentials, database files, customer documents or real financial records.
- Use synthetic data for development and demos.
- Do not ask AI tools to ingest real customer bank statements or identity documents.
- Each sprint ends with a demo and a short list of known limitations.

## Six-week implementation schedule

### Week 1 — Stabilise and foundation

- Contributor A: inspect current auth, remove startup `create_all`, establish migration workflow, finance models and profile API.
- Contributor B: product shell, navigation, profile setup and responsive dashboard frame.
- Contributor C: define exact cash-flow semantics, test cases and interview script.
- Contributor D: conduct 10–15 discovery interviews and synthesise repeated pain points.

**Exit criteria:** clean database migrates to head; legacy database can be safely stamped after schema verification; authenticated user can create/read their profile; no cross-user record access.

### Week 2 — Household ledger

- A: income/expense CRUD, date and amount validation, pagination.
- B: entry form, activity list, filters, loading/error/empty states.
- C: test categories, historical transactions, future expected income, rounding and date boundaries.
- D: observe 5 users entering a week of synthetic or consented sample data.

**Exit criteria:** users can record and correct their own money movements; totals match hand calculations.

### Week 3 — Obligations and Financial Pressure Detector

- A: obligation CRUD/status updates and overview endpoint.
- B: upcoming payments, balance cards and pressure indicator.
- C: verify forecast includes overdue obligations and excludes duplicate future expense entries; document assumptions.
- D: test whether users understand the warning without being frightened or misled.

**Exit criteria:** a fixed set of reference scenarios produces expected balances; all forecasts show a data caveat.

### Week 4 — Small-business ledger

- A: business profile, invoice and payment update APIs.
- B: business mode, sales/expense form, receivables/payables views.
- C: test partial payments, overpayments, overdue invoices and owner isolation.
- D: interview 5–10 local small businesses and validate terminology/workflow.

**Exit criteria:** business user can distinguish cash received from money owed and money payable.

### Week 5 — Reliability and reporting

- A: audit key changes, add export endpoints, tighten validation and rate limits.
- B: monthly summary, CSV export and mobile polish.
- C: API integration tests, migration tests, edge-case suite and manual QA checklist.
- D: recruit pilot users and prepare a plain-language privacy notice and support process.

**Exit criteria:** no known critical data-isolation bug; restore-from-backup procedure documented; CSV matches dashboard totals.

### Week 6 — Controlled pilot

- All: pilot with approximately 20–30 households and 5–10 businesses, with clear consent and a way to stop participation.
- Track onboarding completion, weekly return rate, data-entry burden, usefulness of alerts, calculation errors and support issues.
- Do not collect sensitive documents or connect bank accounts during this pilot.

**Exit criteria:** decide whether users return and whether the product changes a real financial action. If not, revise the problem before adding features.

## MVP success metrics

- At least 60% of pilot users complete initial setup.
- At least 40% return weekly during the pilot.
- 100% of published forecast test cases match expected arithmetic.
- Zero cross-user data access in automated tests.
- Track time to enter a transaction; aim for under 15 seconds after onboarding.
- Record whether a user reports a useful action (planned a payment, followed up a receivable, avoided a missed due date), not just app opens.

## Product safety rules

- Explain that estimates depend on user-entered information and may be incomplete.
- Do not label a record verified unless the verification source is recorded.
- Do not make credit eligibility, investment or legal conclusions.
- For active fraud, direct users to their bank and official reporting channels immediately; never make them finish a chatbot flow first.
- Build consent, data access logs, export and deletion workflows before scaling beyond a small pilot.


## Implementation baseline (current working branch)

The current repository working copy includes the first finance module foundation: profile setup, income/expense entries, household obligations, business profiles, invoice receivables/payables and a 30-day overview endpoint. The overview now accepts `context_type=household|business` and calculates the two contexts independently. Database revision 004 adds check constraints for account modes, entry types, statuses and valid amounts.

### Immediate next tasks (in order)

1. **Contributor A:** add automated API tests for authentication ownership isolation, create/list/update flows, and the household/business overview query parameter. Add database constraints or indexes only through new Alembic revisions.
2. **Contributor B:** complete the mobile layout, add edit flows for entries/obligations/invoices, and make business-entry attribution explicit if the pilot confirms users need multiple separately tracked businesses.
3. **Contributor C:** validate calculations against at least 20 hand-worked household and business scenarios, including overdue items, partial invoices, missing expected income and multiple businesses.
4. **Contributor D:** run 10–15 short interviews and 5 observed onboarding sessions; record exact language people use for money owed, bills, EMIs and available balance.

### Known limitations before a public pilot

- Business income/expense entries are currently grouped at the user's business-context level; invoices are linked to an individual business. Do not interpret the current business overview as a per-business profit statement.
- Recurrence fields are stored but recurring instances are not automatically generated.
- There is no bank, UPI, Account Aggregator or WhatsApp integration.
- The finance API is not yet covered by end-to-end tests in this execution environment. Add those before inviting external users.
- The legacy credit-scoring pages and model remain in the repository during transition; keep them out of the primary user journey until their data validity and intended use have been separately reviewed.
