# AGENTS.md

## Project purpose

This repository contains the HNG 15 Todo application MVP. Build it as a real, maintainable product foundation, not a throwaway demo.

## Working rules

1. Understand before changing. Inspect relevant files and existing architecture before editing.
2. Keep the MVP focused. Do not add features outside the current milestone.
3. Prefer simple, explicit solutions over clever abstractions.
4. Follow existing structure and naming conventions.
5. Keep backend and frontend responsibilities separate.
6. Enforce business rules and authorization on the backend. Never trust the client for security.
7. Every task belongs to a user. A user must never read or modify another user's tasks.
8. Never commit secrets, API keys, passwords, tokens, local databases, or real environment files.
9. Use environment variables for configuration and keep `.env.example` updated.
10. Validate external input at API boundaries and return consistent JSON responses and HTTP status codes.
11. Hash passwords with bcrypt. Never store plaintext passwords.
12. Use database constraints and application validation where appropriate.
13. Write tests for important business rules, especially authentication and authorization.
14. Run relevant tests and checks before considering a change complete.
15. Keep commits small and meaningful. Prefer `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, and `chore:`.
16. Do not rewrite working code merely for stylistic reasons.
17. Do not add a dependency when the standard library or an existing dependency is sufficient.
18. Do not silently change API contracts. Update documentation and tests when contracts change.
19. Keep documentation synchronized with implementation.
20. If requirements are ambiguous, state the assumption before implementing it.

## Architecture

React frontend → Flask REST API → SQLAlchemy → PostgreSQL/Supabase

Authentication uses server-side sessions. The browser manages the HTTP-only session cookie. The React application must not store a session identifier in local storage or application state.

## MVP scope

- User registration, login, logout, and current-user lookup
- Session-based authentication
- Task CRUD
- Explicit task completion state
- Search, filtering, sorting, and pagination
- Due dates
- Categories
- Per-user task isolation

Task priority is not part of the current MVP contract.

## API contract

The authoritative API contract is [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

When changing an endpoint, update the contract and tests in the same change.

## Backend rules

- Organize Flask code by clear responsibility.
- Keep route handlers thin when business logic becomes non-trivial.
- Use SQLAlchemy models for database access.
- Avoid raw SQL unless there is a documented reason.
- Use appropriate HTTP methods and status codes.
- Never expose password hashes or session identifiers.
- Check authentication before protected operations.
- Scope task queries and mutations to the authenticated user.
- Use soft deletion for Tasks by setting `deleted_at`.
- Return 404 for inaccessible tasks instead of revealing another user's resource.
- Completion uses explicit `completed: true|false`, not a toggle.
- Due dates may be null or future timestamps.

## Frontend rules

- Use React components with clear responsibilities.
- Keep API calls in the services layer.
- Handle loading, success, and error states explicitly.
- Send browser credentials with session-authenticated API requests.
- Do not put secrets in frontend environment variables. Anything exposed to a browser is public.
- Keep UI behavior predictable and accessible.

## Git workflow

- `main` is stable.
- `dev` is the integration branch.
- Use focused feature branches, such as `feature/auth` or `feature/tasks`.
- Do not push unfinished experimental work directly to `main`.
- Review the diff before committing.

## Definition of done

A change is complete when:

- It solves the stated requirement.
- It follows the project architecture.
- Relevant tests pass.
- No secrets or generated junk are committed.
- Documentation is updated when behavior or setup changes.
- The API contract matches the implementation.
- The diff is focused and understandable.
