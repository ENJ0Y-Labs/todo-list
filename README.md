# Todo List

A clean, multi-user Todo application built for the HNG 15 Internship and designed as a foundation for a future team task-management product.

## Stack

- Frontend: React
- Backend: Python + Flask
- API: REST + JSON
- ORM: SQLAlchemy
- Database: PostgreSQL via Supabase
- Authentication: Server-side sessions with HTTP-only cookies
- Deployment: Public HTTPS

## MVP features

- User registration, login, logout, and current-user lookup
- Username + password login
- Session-based authentication
- Task CRUD
- Explicit task completion/incompletion
- Search, filtering, sorting, and pagination
- Due dates
- Free-form categories
- Per-user task isolation
- Soft deletion

Priority is intentionally excluded from the current database/API MVP.

## Local setup

Backend:

  cd backend
  python -m venv .venv
  .venv\\Scripts\\Activate.ps1
  pip install -r requirements.txt

Create a backend .env from the root .env.example, configure SECRET_KEY and DATABASE_URL, then apply the schema:

  psql "$DATABASE_URL" -f migrations/001_initial_schema.sql

Start the development server:

  python run.py

Frontend:

  cd frontend
  npm install
  npm run dev

Create frontend/.env from frontend/.env.example when the API URL differs from the default.

## Testing

Backend tests require PostgreSQL and TEST_DATABASE_URL:

  cd backend
  python -m pytest -q

Frontend:

  cd frontend
  npm test
  npm run build

## API

Base path: /api

Authentication:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

Tasks:
- GET /api/tasks
- POST /api/tasks
- GET /api/tasks/<id>
- PATCH /api/tasks/<id>
- DELETE /api/tasks/<id>
- PATCH /api/tasks/<id>/complete

Health:
- GET /api/health

See docs/API_CONTRACT.md for the complete request and response contract.

## Production

The application uses a server-side CacheLib filesystem session store for the MVP. Production deployments must use persistent session storage. For horizontal scaling, use a shared store such as Redis.

Use Gunicorn rather than Flask's development server:

  gunicorn --chdir backend run:app

See docs/DEPLOYMENT.md for the full deployment checklist.

## Development workflow

- main is stable.
- Use focused feature branches.
- Keep commits small and descriptive.
- Review the diff before merging.
- Run relevant tests and checks before opening a pull request.

## Status

Stage: MVP implementation with database migration, backend integration tests, frontend integration, and CI coverage.

The repository is intended to be runnable from a clean PostgreSQL database after applying the migration.

## License

MIT. See LICENSE.
