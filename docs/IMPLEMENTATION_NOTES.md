# Implementation Notes

## Current backend foundation

The Flask backend now exposes the API contract documented in `docs/API_CONTRACT.md`.

The application is organized around:

- `app/auth.py`: authentication routes and authentication guard
- `app/tasks.py`: task routes and task validation
- `app/models.py`: SQLAlchemy models
- `app/extensions.py`: shared Flask extensions
- `app/errors.py`: consistent API error responses
- `app/__init__.py`: application factory

## Session strategy

The MVP uses server-side sessions through Flask-Session.

Local development defaults to filesystem-backed sessions. Production should use a shared server-side store such as Redis and secure cookie settings.

The React client sends `credentials: "include"` on API requests. It never reads or stores the session identifier.

## Database setup

The application expects PostgreSQL through `DATABASE_URL`.

Database migrations are the next infrastructure step. Do not rely on `db.create_all()` for production schema management.

## Validation decisions

- Email is normalized to lowercase.
- Passwords are bcrypt hashes only.
- New tasks are incomplete.
- Due dates must be future timestamps when supplied.
- Task titles are unique among a user's active tasks.
- Task deletion is soft deletion.
- Completion explicitly sets a boolean instead of toggling.
- Task access is always scoped to the authenticated user.
