# API Contract

## Overview

Base path: /api

All API responses are JSON except 204 No Content responses. Authentication uses a server-side session. The browser receives an HTTP-only session cookie and sends it automatically on subsequent requests.

The frontend must send credentials: include for cross-origin authenticated requests.

## Standard error format

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required."
  }
}

Common codes:

| HTTP | Code | Meaning |
|---:|---|---|
| 400 | VALIDATION_ERROR | Request data is invalid |
| 401 | AUTHENTICATION_REQUIRED | No valid session |
| 401 | INVALID_CREDENTIALS | Login credentials are invalid |
| 403 | ACCOUNT_SUSPENDED | Account is suspended |
| 404 | RESOURCE_NOT_FOUND | Resource is unavailable to this user |
| 409 | EMAIL_ALREADY_REGISTERED | Email already exists |
| 409 | USERNAME_ALREADY_REGISTERED | Username already exists |
| 409 | TASK_TITLE_ALREADY_EXISTS | Active task title already exists for this user |
| 405 | METHOD_NOT_ALLOWED | HTTP method is unsupported |

## Authentication

### POST /api/auth/register

Creates a user and immediately authenticates the new user.

Request:

{
  "email": "jerry@example.com",
  "password": "strong-password",
  "username": "jerry",
  "fullname": "Jerry Example"
}

Required fields: email, password, username, fullname.

Rules:
- Email is normalized to lowercase.
- Username uniqueness is case-insensitive.
- Password must be at least 8 characters.
- Email must not exceed 255 characters.
- Username must not exceed 100 characters.
- Full name must not exceed 150 characters.
- Duplicate active emails return 409 EMAIL_ALREADY_REGISTERED.
- Duplicate active usernames return 409 USERNAME_ALREADY_REGISTERED.
- Password is hashed before storage.
- A new server-side session is created.

Response: 201 Created

{
  "user": {
    "id": "uuid",
    "email": "jerry@example.com",
    "username": "jerry",
    "fullname": "Jerry Example",
    "status": "active",
    "created_at": "2026-09-28T18:00:00+00:00",
    "updated_at": "2026-09-28T18:00:00+00:00"
  },
  "authenticated": true
}

### POST /api/auth/login

Login uses username and password only.

Request:

{
  "username": "jerry",
  "password": "strong-password"
}

Username matching is case-insensitive.

Response: 200 OK

The response shape is the same as registration. A new authenticated session is created.

### POST /api/auth/logout

Clears the current server-side session.

Response: 204 No Content.

### GET /api/auth/me

Returns the currently authenticated user.

Response: 200 OK

{
  "user": {
    "id": "uuid",
    "email": "jerry@example.com",
    "username": "jerry",
    "fullname": "Jerry Example",
    "status": "active",
    "created_at": "2026-09-28T18:00:00+00:00",
    "updated_at": "2026-09-28T18:00:00+00:00"
  },
  "authenticated": true
}

Unauthenticated: 401 AUTHENTICATION_REQUIRED.

## Tasks

### Task object

{
  "id": "uuid",
  "title": "Study Flask",
  "description": "Review blueprints",
  "completed": false,
  "due_at": "2026-09-30T18:00:00+00:00",
  "category": "school",
  "created_at": "2026-09-28T18:00:00+00:00",
  "updated_at": "2026-09-28T18:00:00+00:00"
}

description, due_at, and category may be null.

### POST /api/tasks

Creates a task for the authenticated user.

Request:

{
  "title": "Study Flask",
  "description": "Review blueprints",
  "due_at": "2026-09-30T18:00:00+00:00",
  "category": "school"
}

Only title is required.

Rules:
- New tasks always start as completed=false.
- Title must be 1–255 characters.
- Description may be null and is limited to 5000 characters.
- Category may be null and is limited to 100 characters.
- due_at may be null but cannot be in the past.
- Active task titles must be unique per user.
- Unknown request fields are rejected with 400 VALIDATION_ERROR.
- The `completed` field cannot be supplied when creating or updating task content; use the completion endpoint.

Response: 201 Created

{
  "task": { "Task object": "..." }
}

### GET /api/tasks

Returns the authenticated user's active tasks.

Default request: /api/tasks?page=1&per_page=20

Supported query parameters:

| Parameter | Values | Default |
|---|---|---|
| page | integer >= 1 | 1 |
| per_page | 1–100 | 20 |
| search | text | none |
| completed | true/false | all |
| category | text | all |
| due_after | ISO 8601 datetime | none |
| due_before | ISO 8601 datetime | none |
| sort | title, due_at, created_at, updated_at | created_at |
| order | asc, desc | desc |

search checks title, description, and category using case-insensitive substring matching.

Category filtering is case-insensitive.

When sorting by `due_at`, tasks without a due date are always placed after tasks with due dates, for both ascending and descending order.

Response: 200 OK

{
  "tasks": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 0,
    "total_pages": 0
  }
}

### GET /api/tasks/<id>

Returns one active task owned by the authenticated user.

Response: 200 OK

{
  "task": { "Task object": "..." }
}

If the task does not belong to the authenticated user or has been deleted: 404 RESOURCE_NOT_FOUND.

### PATCH /api/tasks/<id>

Updates task content.

Allowed fields:
- title
- description
- due_at
- category

Not allowed:
- id
- completed
- created_at
- updated_at

Completion has its own endpoint.

An empty PATCH body is invalid and returns 400 VALIDATION_ERROR.

Response: 200 OK with the updated task.

### PATCH /api/tasks/<id>/complete

Explicitly sets completion state. It does not toggle.

Request:

{
  "completed": true
}

Response: 200 OK

{
  "task": {
    "id": "uuid",
    "completed": true,
    "updated_at": "2026-09-28T18:00:00+00:00"
  }
}

### DELETE /api/tasks/<id>

Soft-deletes the task by setting deleted_at.

Response: 204 No Content.

Deleted tasks are excluded from normal API queries.

## Ownership and security

Every protected task query is scoped by the authenticated user. The API never trusts a client-supplied user_id.

Password hashes and session identifiers are never returned.

## Session cookie and deployment

The session cookie is HTTP-only. SameSite defaults to Lax and should remain Lax when the frontend and API are deployed on the same site. Production HTTPS deployments should set SESSION_COOKIE_SECURE=true.

If the frontend and API must be deployed on different sites, use SameSite=None with Secure cookies and add an explicit CSRF protection mechanism before enabling state-changing cross-site requests.

The recommended deployment shape is same-site frontend/API hosting, such as app.example.com and api.example.com, rather than unrelated domains.

## Implementation order

1. Database migration/schema
2. Authentication tests
3. Task CRUD tests
4. Authorization and ownership tests
5. Frontend service integration
6. Deployment configuration
