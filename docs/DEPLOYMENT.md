# Deployment

## Local backend

cd backend
python -m venv .venv

Windows PowerShell:

.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py

Backend development port: 5000.

## Local frontend

cd frontend
npm install
npm run dev

Frontend development port: 5173.

## Environment

Keep real environment values outside Git.

Never commit:
- database passwords
- session secrets
- API keys
- tokens
- real .env files
- local databases containing user data

Backend tests use TEST_DATABASE_URL.

Frontend uses VITE_API_BASE_URL for the API origin/path.

## Production topology

Browser -> HTTPS frontend -> HTTPS Flask API -> PostgreSQL

A same-site arrangement such as app.example.com and api.example.com is recommended because it simplifies cookie behavior.

## Session cookies

Authentication uses a server-side session and HTTP-only cookie.

For production HTTPS, set SESSION_COOKIE_SECURE=true.

For same-site frontend/API deployment, SameSite=Lax should generally remain enabled.

For genuinely cross-site frontend/API deployment, SameSite=None and Secure are required for the cookie. Add explicit CSRF protection before allowing state-changing cross-site requests.

React must never receive or store the session identifier.

## Database

PostgreSQL is the required MVP database. Supabase may host it, but application code should keep PostgreSQL as the database contract.

Before production:
1. Create the production database.
2. Apply schema/migrations.
3. Configure a strong session secret.
4. Enable secure session cookies.
5. Restrict database credentials to the backend.
6. Run tests against a representative PostgreSQL version.
7. Verify CORS and cookie behavior.
8. Verify startup/health behavior.
9. Confirm no secrets are present in frontend output.

## Deployment checklist

- [ ] HTTPS enabled.
- [ ] Production database configured.
- [ ] Schema/migrations applied.
- [ ] Strong session secret configured.
- [ ] Secure HTTP-only cookie enabled.
- [ ] CORS restricted to the real frontend origin.
- [ ] CSRF protection added for cross-site state-changing requests.
- [ ] Frontend API URL points to production.
- [ ] No secrets committed.
- [ ] Backend tests pass.
- [ ] Frontend tests pass.
- [ ] Production build succeeds.
- [ ] Browser authentication verified.
- [ ] Cross-user task isolation verified.
