# Todo List

A clean, multi-user Todo application built for the HNG 15 Internship and designed as a foundation for a future team task-management product.

## Stack

- Frontend: React
- Backend: Python + Flask
- API: REST + JSON
- ORM: SQLAlchemy
- Database: PostgreSQL via Supabase
- Authentication: Server-side sessions
- Deployment: Public HTTPS

## Planned features

- User registration, login, and logout
- Session-based authentication
- Create, view, update, and delete tasks
- Mark tasks as complete
- Search, filtering, and sorting
- Task priorities
- Due dates
- Categories/tags
- Per-user task isolation

## Project structure

```text
todo-list/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── hooks/
├── .env.example
├── .gitignore
├── AGENTS.md
├── README.md
└── LICENSE
```

## Development workflow

- `main` is the stable branch.
- `dev` is the integration branch.
- Create focused feature branches from `dev`.
- Keep commits small and descriptive.
- Run relevant tests and checks before opening a pull request.

## Local setup

The application is currently being scaffolded. Setup instructions will be expanded as implementation progresses.

Expected architecture:

```text
React → Flask REST API → SQLAlchemy → PostgreSQL/Supabase
```

## Environment variables

Copy `.env.example` to a local `.env` file and replace the placeholder values. Never commit `.env` or production secrets.

## Project rules

See [AGENTS.md](AGENTS.md) for the development, security, testing, architecture, and Git workflow rules.

## Status

**Stage:** Initial project scaffolding

The first implementation milestone is a working Flask backend with a basic health/hello endpoint. Database models and authentication will follow incrementally.

## License

MIT. See [LICENSE](LICENSE).
