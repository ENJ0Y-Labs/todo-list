# AGENTS.md

## Project purpose

This repository contains the HNG 15 Todo application MVP. Build it as a real, maintainable product foundation, not a throwaway demo.

## Working rules

1. Understand before changing. Inspect relevant files and existing architecture before editing.
2. Keep the MVP focused.
3. Prefer simple, explicit solutions over clever abstractions.
4. Keep backend and frontend responsibilities separate.
5. Enforce business rules and authorization on the backend.
6. Every task belongs to a user and must be ownership-scoped.
7. Never commit secrets, passwords, tokens, local databases, or real environment files.
8. Use environment variables for configuration.
9. Validate input at API boundaries and return consistent JSON errors.
10. Hash passwords. Never store plaintext passwords.
11. Use database constraints and application validation.
12. Write tests for authentication, validation, authorization, and ownership.
13. Run relevant tests before considering a change complete.
14. Keep commits small and meaningful.
15. Do not silently change API contracts. Update documentation and tests.
16. Keep documentation synchronized with implementation.
17. If requirements are ambiguous, state the assumption before implementing it.

## Architecture

React frontend -> Flask REST API -> SQLAlchemy -> PostgreSQL/Supabase

Authentication uses server-side sessions. The browser receives an HTTP-only session cookie. The frontend does not manage a session ID in application state.

## MVP scope

- User registration, login, logout, and current-user lookup
- Session-based authentication
- Task CRUD
- Explicit task completion/incompletion
- Search, filtering, sorting, and pagination
- Due dates
- Free-form categories
- Per-user task isolation
- Soft deletion

Task priority is deferred and must not be added without an explicit product decision.

## API contract rules

- Base path is /api.
- JSON is used for request and response bodies except 204 responses.
- Authentication uses an HTTP-only server-side session cookie.
- Protected endpoints require an authenticated active user.
- User emails are normalized to lowercase.
- Registration requires email, password, username, and fullname.
- Registration immediately creates an authenticated session.
- Duplicate emails return 409 EMAIL_ALREADY_REGISTERED.
- New tasks always start with completed=false.
- Task PATCH changes title, description, due_at, and category only.
- Completion uses PATCH /api/tasks/<id>/complete with an explicit boolean.
- Completion does not toggle.
- Task deletion is soft deletion through deleted_at.
- Task access is always scoped to the authenticated owner.
- A task belonging to another user is exposed as 404 RESOURCE_NOT_FOUND.
- Task listing uses pagination and documented query parameters.
- Errors use { error: { code, message } }.

## Backend rules

- Organize Flask code by responsibility.
- Use SQLAlchemy models for database access.
- Avoid raw SQL unless there is a documented reason.
- Use appropriate HTTP methods and status codes.
- Never expose password hashes or session identifiers.
- Check authentication before protected operations.

## Frontend rules

- Keep API calls in the services layer.
- Use credentials: include for authenticated API calls.
- Handle loading, success, and error states explicitly.
- Do not put secrets in frontend environment variables.

## Git workflow

- main is stable.
- Use focused feature branches.
- Do not push unfinished experimental work directly to main.
- Review the diff before committing.

## Definition of done

A change is complete when it solves the requirement, follows the architecture, passes relevant tests, contains no secrets, updates documentation when behavior changes, and has a focused diff.
