# Deployment

## Local backend

cd backend
python -m venv .venv

Windows PowerShell:

.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Create a real backend .env from the root .env.example, then run:

python run.py

Backend development port: 5000.

## Local frontend

cd frontend
npm install
npm run dev

Frontend development port: 5173.

Create frontend/.env from frontend/.env.example when the API is not at the default local URL.

## Environment

Keep real environment values outside Git.

Never commit:
- database passwords
- session secrets
- API keys
- tokens
- real .env files
- local databases containing user data

Required backend values:
- SECRET_KEY
- DATABASE_URL
- CORS_ORIGINS

Backend tests require TEST_DATABASE_URL.

Frontend uses VITE_API_BASE_URL from frontend/.env.

## Database migrations

PostgreSQL is the required MVP database. Supabase may host it, but application code keeps PostgreSQL as the database contract.

For a fresh database:

psql "$DATABASE_URL" -f backend/migrations/001_initial_schema.sql

The migration creates users, tasks, indexes, and constraints. The application does not run database DDL at startup.

## Production topology

Browser -> HTTPS frontend -> HTTPS Flask API -> PostgreSQL

A same-site arrangement such as app.example.com and api.example.com is recommended because it simplifies cookie behavior.

## Server-side sessions

Authentication uses server-side sessions backed by CacheLib's filesystem store for this MVP. The browser receives only an HTTP-only session cookie.

Set SESSION_FILE_DIR to a persistent directory in production. For multiple backend instances, replace the filesystem store with a shared CacheLib/Redis store before scaling horizontally.

For production HTTPS, set SESSION_COOKIE_SECURE=true.

For same-site frontend/API deployment, SameSite=Lax should generally remain enabled.

For genuinely cross-site frontend/API deployment, SameSite=None and Secure are required for the cookie. Add explicit CSRF protection before allowing state-changing cross-site requests.

## Production server

Do not use Flask's development server in production.

Run the application with Gunicorn, for example:

gunicorn --chdir backend run:app

The application reads FLASK_DEBUG=0 by default. Never enable the Werkzeug debugger on a public service.

## Pre-deployment checklist

- [ ] HTTPS enabled.
- [ ] Production database configured.
- [ ] Schema migration applied.
- [ ] Strong SECRET_KEY configured.
- [ ] Persistent server-side session storage configured.
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
