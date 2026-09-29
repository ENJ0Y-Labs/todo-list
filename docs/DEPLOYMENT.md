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

For the Vercel production deployment, set:

VITE_API_BASE_URL=/api

This value is baked into the frontend at build time, so redeploy Vercel after changing it.

## Database migrations

PostgreSQL is the required MVP database. Supabase may host it, but application code keeps PostgreSQL as the database contract.

For a fresh database:

psql "$DATABASE_URL" -f backend/migrations/001_initial_schema.sql

The migration creates users, tasks, indexes, and constraints. The application does not run database DDL at startup.

## Production topology

The production frontend uses a Vercel rewrite so browser API requests remain same-origin:

Browser -> Vercel frontend (/api) -> Render Flask API -> PostgreSQL

frontend/vercel.json proxies /api/* to the Render backend and rewrites other paths to /index.html so React Router routes such as /dashboard work on refresh.

The frontend API base URL must therefore be /api in Vercel.

## Server-side sessions

Authentication uses server-side sessions backed by CacheLib's filesystem store for this MVP. The browser receives only an HTTP-only session cookie.

Set SESSION_FILE_DIR to a persistent directory in production. For multiple backend instances, replace the filesystem store with a shared CacheLib/Redis store before scaling horizontally.

For the Vercel same-origin proxy deployment, use:

SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax

Keep CORS restricted to the real frontend origin when the backend is also directly reachable:

CORS_ORIGINS=https://todo-list-murex-chi.vercel.app

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
- [ ] Frontend Vercel API URL is /api.
- [ ] Vercel deployment uses frontend/vercel.json.
- [ ] No secrets committed.
- [ ] Backend tests pass.
- [ ] Frontend tests pass.
- [ ] Production build succeeds.
- [ ] Browser authentication verified.
- [ ] Cross-user task isolation verified.
