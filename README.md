# Todo List

A clean, public Stage 1 Todo application built for the HNG 15 Internship.

## Stage 1 demo

The deployed frontend is intentionally public and requires no login. Reviewers can open the app and immediately test task creation, editing, completion, deletion, filtering, sorting, and sample data.

Task data for the public demo is stored in the browser's local storage, so the demo does not depend on authentication cookies or a backend session.

Use **Load sample data** to populate the app with representative tasks. Use **Clear all data** to return to the empty state.

## Stack

- Frontend: React + Vite
- Backend: Python + Flask
- API: REST + JSON
- ORM: SQLAlchemy
- Database: PostgreSQL via Supabase
- Original backend authentication: server-side sessions with HTTP-only cookies

## MVP features

- Create, edit, complete, reopen, and delete tasks
- Search and filter tasks
- Sort tasks
- Categories
- Due dates
- Empty state
- Sample data loading
- Browser persistence for the public Stage 1 demo

## Local setup

Frontend:

  cd frontend
  npm install
  npm run dev

Backend development and the original authenticated API remain available for continued project development. See `docs/DEPLOYMENT.md` and `docs/API_CONTRACT.md`.

## Testing

Frontend:

  npm test
  npm run build

Backend:

  cd backend
  python -m pytest -q

## Repository rules

See `AGENTS.md` for the project development rules. Do not commit secrets or real environment files.

## License

MIT. See LICENSE.
