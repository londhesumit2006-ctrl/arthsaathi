# ArthSaathi website — implementation notes

## Routes

- `/` — public product landing page; redirects to `/money` when signed in
- `/login` — user login
- `/register` — account registration
- `/money` — authenticated ArthSaathi workspace
- Legacy credit application and admin routes remain available during migration

## Workspace navigation

1. Overview
2. Household finances
3. Small business
4. Debt & loan planner
5. Savings planner
6. Financial safety
7. Schemes & support
8. Document helper
9. Money guide
10. Monthly report
11. Settings

## Persistence boundaries

### Backend-persisted

- Financial profile and current balance
- Household and business income/expense entries
- Upcoming obligations
- Business profiles
- Business invoices and payment updates

### Browser-local only

- Savings planner inputs
- Document text pasted into the document helper (not sent to the API)
- Current navigation state and calculator inputs

The frontend should not imply that browser-local information is backed up or synchronised to another device.

## External resources

The safety page links to the National Cyber Crime Reporting Portal, 1930 dial action and RBI CMS. The schemes page links to official government portals such as myScheme, PMJDY, PM SVANidhi, Udyam, National Scholarship Portal, e-Shram and Jan Suraksha. Links and eligibility details must be rechecked before each public release.

## Before pilot release

- Add API integration tests for all finance endpoints.
- Verify cross-user data isolation for entries, obligations, businesses and invoices.
- Add a user-visible account deletion/data export flow.
- Review authentication token storage and session expiry.
- Add backend persistence for savings goals if cross-device access is required.
- Add server-side document processing only after privacy, consent, file safety and retention rules are implemented.
- Integrate WhatsApp only after obtaining a verified business account, approved templates where needed, privacy notice and consent flow.
- Review all external scheme links and financial guidance.
- Test keyboard navigation, screen readers, low-bandwidth use and Hindi typography.
