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

## Current MVP

- User registration, login, logout, and current-user lookup
- Session-based authentication
- Task CRUD
- Explicit task completion
- Search, filtering, sorting, and pagination
- Due dates
- Categories
- Per-user task isolation
- Soft deletion

Task priority is deliberately outside the current MVP contract.

## Project structure

```text
todo-list/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── errors.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   └── tasks.py
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── hooks/
├── docs/
│   ├── API_CONTRACT.md
│   └── DATABASE_DESIGN.md
├── .env.example
├── .gitignore
├── AGENTS.md
├── README.md
└── LICENSE
```

## API

Base path:

```text
/api
```

Authentication:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

Tasks:

```text
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/<id>
PATCH  /api/tasks/<id>
DELETE /api/tasks/<id>
PATCH  /api/tasks/<id>/complete
```

The complete request/response contract is documented in [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

## Local setup

1. Create a Python virtual environment.
2. Install backend dependencies:

```bash
cd backend
python -m pip install -r requirements.txt
```

3. Create a local `.env` from `.env.example`.
4. Set `DATABASE_URL` to a PostgreSQL database.
5. Run the Flask application:

```bash
python run.py
```

The API will be available at `http://localhost:5000/api`.

## Environment variables

Copy `.env.example` to `.env` and replace placeholders. Never commit `.env` or production secrets.

## Development workflow

- `main` is the stable branch.
- `dev` is the integration branch.
- Create focused feature branches from `dev`.
- Keep commits small and descriptive.
- Run relevant tests and checks before opening a pull request.

## Documentation

- [API Contract](docs/API_CONTRACT.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [Agent rules](AGENTS.md)

## Status

**Stage:** API contract defined and Flask endpoint foundation implemented.

The next implementation work is database migrations, automated tests, frontend API integration, and deployment configuration.

## License

MIT. See [LICENSE](LICENSE).
