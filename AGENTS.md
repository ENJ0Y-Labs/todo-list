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
11. Hash passwords with a suitable password-hashing library. Never store plaintext passwords.
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

Authentication uses server-side sessions. The frontend communicates with the backend through the documented REST API.

## MVP scope

- User registration, login, and logout
- Session-based authentication
- Task CRUD
- Task completion
- Search, filtering, and sorting
- Priorities
- Due dates
- Categories/tags
- Per-user task isolation

Do not add unrelated features until the MVP requirements are stable.

## Backend rules

- Organize Flask code by clear responsibility.
- Keep route handlers thin when business logic becomes non-trivial.
- Use SQLAlchemy models for database access.
- Avoid raw SQL unless there is a documented reason.
- Use appropriate HTTP methods and status codes.
- Never expose password hashes or sensitive session information.
- Check authentication before protected operations.
- Scope task queries and mutations to the authenticated user.

## Frontend rules

- Use React components with clear responsibilities.
- Keep API calls in the services layer.
- Handle loading, success, and error states explicitly.
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
- The diff is focused and understandable.
