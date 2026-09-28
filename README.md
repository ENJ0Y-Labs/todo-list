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
- Session-based authentication
- Task CRUD
- Explicit task completion/incompletion
- Search, filtering, sorting, and pagination
- Due dates
- Free-form categories
- Per-user task isolation
- Soft deletion

Priority is intentionally excluded from the current database/API MVP.

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

The complete request/response contract is documented in docs/API_CONTRACT.md.

## Project structure

todo-list/
  backend/
    app/
      routes/
        auth.py
        tasks.py
      errors.py
      extensions.py
      models.py
      utils.py
    tests/
    requirements.txt
    run.py
  frontend/
    src/
      components/
      pages/
      services/
        api.js
      hooks/
  docs/
    API_CONTRACT.md
    DATABASE_DESIGN.md
  .env.example
  .gitignore
  AGENTS.md
  README.md
  LICENSE

## Local setup

Backend:

  cd backend
  python -m venv .venv
  .venv\\Scripts\\Activate.ps1
  pip install -r requirements.txt
  python run.py

Set the variables in .env before running the backend. The backend expects PostgreSQL.

The frontend API client uses credentials: include so the browser sends the server-side session cookie.

## Development workflow

- main is stable.
- Use focused feature branches.
- Keep commits small and descriptive.
- Review the diff before merging.
- Run relevant tests and checks before opening a pull request.

## Status

Stage: API contract + backend endpoint implementation

Next milestone: database migrations, automated API tests, and frontend integration.

## License

MIT. See LICENSE.
