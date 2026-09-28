# Architecture

## System

React frontend -> Flask REST API -> SQLAlchemy -> PostgreSQL

Authentication uses server-side sessions. The browser stores an HTTP-only session cookie. React stores the authenticated user object, not a session identifier.

## Frontend responsibilities

- Render authentication and dashboard screens.
- Collect and validate user input.
- Maintain current user through AuthContext.
- Maintain task UI state locally.
- Send HTTP requests only through services/api.js.
- Display loading, success, error, and empty states.
- Handle client-side routing and protected routes.

The frontend has no database access and must not contain secrets.

## Backend responsibilities

- Authentication and authorization.
- Session creation and destruction.
- Input validation.
- Business rules.
- Task ownership enforcement.
- SQLAlchemy database operations.
- HTTP status codes and JSON error responses.
- Safe serialization of User and Task data.

The backend is the security boundary.

## Database responsibilities

PostgreSQL provides persistent storage, UUID keys, foreign keys, uniqueness constraints, indexes, timestamps, and soft-deletion fields.

## Registration flow

1. Frontend sends email, password, username, and fullname.
2. Backend validates and normalizes input.
3. Password is hashed.
4. User is persisted.
5. A server-side session is created.
6. Safe user data is returned.
7. AuthContext stores the user.
8. Frontend navigates to the dashboard.

## Login flow

1. Frontend sends username and password.
2. Backend performs case-insensitive username lookup.
3. Backend checks the password hash.
4. Backend rejects suspended or deleted accounts.
5. Backend creates a fresh authenticated session.
6. Frontend stores the user.

## Startup authentication

AuthContext calls GET /api/auth/me when the app starts. While that request is pending, the app displays an authentication spinner. AuthGate then redirects users according to authentication state.

## Task ownership

Every protected task query is scoped to the authenticated user.

Creation always assigns the authenticated user's ID. Client-supplied user_id is ignored and cannot change ownership.

A task belonging to another user is returned as 404 RESOURCE_NOT_FOUND for reads, updates, completion, and deletion.

## Task lifecycle

Created -> active incomplete -> active complete -> edited

Any active task can also become soft deleted.

Completion uses PATCH /api/tasks/<id>/complete with an explicit boolean. It does not toggle.

Deletion sets deleted_at. Normal queries exclude deleted records.

## Error flow

The API uses:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required."
  }
}

The frontend maps common backend errors to user-friendly messages and falls back to the backend message when needed.

## Repository boundaries

backend/app/routes contains HTTP endpoints.
backend/app/errors.py contains API error handling.
backend/app/extensions.py contains Flask and SQLAlchemy extensions.
backend/app/models.py contains database models.
backend/app/utils.py contains shared helpers.
backend/tests contains backend tests.
backend/run.py is the development entry point.

frontend/src/pages contains route-level screens.
frontend/src/context contains authentication state.
frontend/src/services contains the HTTP client.
frontend/src/test contains test setup.
frontend/src/global.css contains global styling.
frontend/src/App.jsx contains routing and auth gates.
frontend/src/main.jsx is the React entry point.

docs contains project documentation.

## Design principles

- Keep the MVP small.
- Prefer explicit solutions over clever abstractions.
- Enforce authorization on the backend.
- Keep all frontend HTTP calls in one service.
- Use database constraints as a second integrity layer.
- Do not add features without a product decision.
