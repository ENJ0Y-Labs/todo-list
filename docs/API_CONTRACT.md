# API Contract

## Purpose

This document is the contract between the React frontend and Flask backend. Routes, request bodies, response bodies, validation rules, and status codes should stay synchronized with the implementation.

## Base URL

Local API base:

`/api`

All JSON request bodies use `Content-Type: application/json`.

Authentication uses server-side sessions. The backend sets an HTTP-only session cookie; the frontend does not store or send a session ID manually. Browser requests must allow credentials when the frontend and API are on different origins.

## Authentication

### POST /api/auth/register

Creates a user and immediately authenticates the new user.

Request:

```json
{
  "email": "jerry@example.com",
  "password": "strong-password",
  "username": "jerry",
  "fullname": "Jerry Example"
}
```

Rules:
- All four fields are required.
- Email is normalized to lowercase.
- Email must be unique.
- Password is stored only as a password hash.
- A new user starts with `active` status.
- A successful registration creates a server-side session.

Success: `201 Created`

Response:

```json
{
  "user": {
    "id": "uuid",
    "email": "jerry@example.com",
    "username": "jerry",
    "fullname": "Jerry Example",
    "status": "active",
    "created_at": "2026-09-28T18:00:00Z",
    "updated_at": "2026-09-28T18:00:00Z"
  }
}
```

Errors:
- `400 VALIDATION_ERROR`
- `409 EMAIL_ALREADY_REGISTERED`

### POST /api/auth/login

Authenticates an existing active user and creates a server-side session.

Request:

```json
{
  "email": "jerry@example.com",
  "password": "strong-password"
}
```

Success: `200 OK`

Response:

```json
{
  "user": {
    "id": "uuid",
    "email": "jerry@example.com",
    "username": "jerry",
    "fullname": "Jerry Example",
    "status": "active",
    "created_at": "2026-09-28T18:00:00Z",
    "updated_at": "2026-09-28T18:00:00Z"
  }
}
```

Errors:
- `400 VALIDATION_ERROR`
- `401 INVALID_CREDENTIALS`
- `403 ACCOUNT_SUSPENDED`

### POST /api/auth/logout

Requires authentication. Invalidates the current server-side session and clears the session cookie.

Success: `204 No Content`

### GET /api/auth/me

Returns the currently authenticated user.

Success: `200 OK`

Response:

```json
{
  "user": {
    "id": "uuid",
    "email": "jerry@example.com",
    "username": "jerry",
    "fullname": "Jerry Example",
    "status": "active",
    "created_at": "2026-09-28T18:00:00Z",
    "updated_at": "2026-09-28T18:00:00Z"
  }
}
```

Unauthenticated: `401 AUTHENTICATION_REQUIRED`

## Tasks

All task endpoints require authentication. Every query is scoped to the authenticated user.

Task response shape:

```json
{
  "id": "uuid",
  "title": "Study Flask",
  "description": "Review Flask blueprints",
  "completed": false,
  "due_at": "2026-09-30T18:00:00Z",
  "category": "school",
  "created_at": "2026-09-28T18:00:00Z",
  "updated_at": "2026-09-28T18:00:00Z"
}
```

### GET /api/tasks

Returns active tasks using pagination.

Query parameters:

- `page`: positive integer, default `1`
- `per_page`: positive integer, default `20`, maximum `100`
- `search`: searches task title and description
- `completed`: `true` or `false`
- `category`: exact category filter
- `due_before`: ISO-8601 timestamp
- `due_after`: ISO-8601 timestamp
- `sort`: `created_at`, `updated_at`, `due_at`, or `title`
- `order`: `asc` or `desc`

Success: `200 OK`

```json
{
  "tasks": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 0,
    "total_pages": 0
  }
}
```

### POST /api/tasks

Creates an active task.

Request:

```json
{
  "title": "Study Flask",
  "description": "Review Flask blueprints",
  "completed": false,
  "due_at": "2026-09-30T18:00:00Z",
  "category": "school"
}
```

Rules:
- `title` is required.
- `description`, `due_at`, and `category` are optional.
- New tasks default to `completed: false`; clients should normally omit `completed`.
- `due_at` may be null or a future timestamp. Past due dates are rejected.
- Category is free-form text.
- Task title is limited to 255 characters.
- Description is limited to 5000 characters.
- An active user cannot have duplicate active task titles.

Success: `201 Created`

Errors:
- `400 VALIDATION_ERROR`
- `409 TASK_TITLE_ALREADY_EXISTS`

### GET /api/tasks/<id>

Returns one active task owned by the authenticated user.

Success: `200 OK`

If the task does not exist, is soft-deleted, or belongs to another user: `404 RESOURCE_NOT_FOUND`.

### PATCH /api/tasks/<id>

Partially updates task information.

Allowed fields:
- `title`
- `description`
- `due_at`
- `category`

The fields `id`, `created_at`, `updated_at`, `user_id`, `deleted_at`, and `completed` cannot be changed here.

Success: `200 OK`

The same title, description, and due-date validation rules as creation apply.

### PATCH /api/tasks/<id>/complete

Explicitly sets completion state.

Request:

```json
{
  "completed": true
}
```

The value must be boolean. Explicit state is used instead of toggling so retried requests remain idempotent.

Success: `200 OK`

Response:

```json
{
  "id": "uuid",
  "completed": true,
  "updated_at": "2026-09-28T18:00:00Z"
}
```

### DELETE /api/tasks/<id>

Soft-deletes the active task by setting `deleted_at`.

Success: `204 No Content`

A deleted task is excluded from normal task queries.

## Error Format

Every API error uses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required"
  }
}
```

Standard codes:

| HTTP | Code | Meaning |
|---|---|---|
| 400 | VALIDATION_ERROR | Request data is invalid |
| 401 | AUTHENTICATION_REQUIRED | Login is required |
| 401 | INVALID_CREDENTIALS | Email/password combination is invalid |
| 403 | ACCOUNT_SUSPENDED | Account is not allowed to authenticate |
| 404 | RESOURCE_NOT_FOUND | Resource is unavailable to the current user |
| 409 | EMAIL_ALREADY_REGISTERED | Email is already in use |
| 409 | TASK_TITLE_ALREADY_EXISTS | Active task title already exists for this user |

## Security Rules

- Never return password hashes.
- Never return server-side session identifiers in JSON.
- Authentication state is represented by the server-side session cookie.
- Task access is always scoped to the authenticated user.
- Do not reveal whether another user's task exists.
- Normalize emails before lookup and persistence.
