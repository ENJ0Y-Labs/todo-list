# Database Design

## MVP Database Decisions

This document defines the database model used by the Flask API.

### Database

- PostgreSQL
- UUID primary keys
- `TIMESTAMPTZ` for timestamps
- Singular entity/table naming
- Database-level foreign-key and integrity constraints

## User

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| email | VARCHAR(255) | Required, unique, normalized to lowercase |
| password_hash | TEXT | Required; only the hash is stored |
| username | VARCHAR(100) | Required, unique |
| fullname | VARCHAR(255) | Required |
| status | constrained value | `active` or `suspended` |
| created_at | TIMESTAMPTZ | Required |
| updated_at | TIMESTAMPTZ | Required |
| deleted_at | TIMESTAMPTZ | Nullable; soft deletion |

Email verification is deferred until after the MVP.

Soft-deleted users are not represented by a separate status. `deleted_at` handles deletion state.

## Task

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Required foreign key to User |
| title | VARCHAR(255) | Required |
| description | TEXT | Nullable; API maximum 5000 characters |
| completed | BOOLEAN | Required, defaults to `false` |
| due_at | TIMESTAMPTZ | Nullable; API rejects past values |
| category | VARCHAR(100) | Nullable; free-form text |
| created_at | TIMESTAMPTZ | Required |
| updated_at | TIMESTAMPTZ | Required |
| deleted_at | TIMESTAMPTZ | Nullable; soft deletion |

Priority is intentionally excluded from the MVP.

Category remains a simple field on Task rather than a separate Category entity.

## Relationship

One User owns many Tasks. Every Task belongs to exactly one User.

```
User 1 ─────────── * Task
```

The `tasks.user_id` foreign key is `NOT NULL` and uses `ON DELETE CASCADE`.

Deleting a User permanently deletes all associated Tasks. This is intentionally different from normal Task deletion, which uses soft deletion.

## Integrity Rules

### User email

```
email UNIQUE NOT NULL
```

Application logic normalizes emails to lowercase before lookup and persistence.

### Username

Username is required and unique.

### Task ownership

```
user_id UUID NOT NULL
FOREIGN KEY → users.id
ON DELETE CASCADE
```

### Task completion

```
completed BOOLEAN NOT NULL DEFAULT FALSE
```

### Task title

```
title VARCHAR(255) NOT NULL
```

Active tasks belonging to the same user cannot have duplicate titles.

Because Tasks use soft deletion, PostgreSQL should enforce title uniqueness only where `deleted_at IS NULL`.

### Due date

```
due_at TIMESTAMPTZ NULL
```

The due date is optional. API validation rejects a due timestamp in the past.

### Soft deletion

Both Users and Tasks support:

```
deleted_at TIMESTAMPTZ NULL
```

Normal application queries exclude records where `deleted_at IS NOT NULL`.

## Timestamps

All entities use:

- `created_at`: creation timestamp
- `updated_at`: last modification timestamp
- `deleted_at`: nullable soft-deletion timestamp where applicable

The implementation updates `updated_at` when a record changes.

## Indexing

Initial indexes support:

- User email lookup
- Username lookup
- Tasks by user
- Active tasks by user
- Due-date filtering/sorting
- Category filtering

Indexes should be added deliberately rather than indiscriminately.

## Deferred Features

- Email verification
- Password reset tokens
- Task priority
- Separate Category table
- Team members/assignees
- Task assignment
- Advanced roles/permissions
- Audit/event history

These should be introduced through migrations when requirements justify them.

## Implementation Order

1. Finalize PostgreSQL schema.
2. Add UUID generation.
3. Add constraints and indexes.
4. Add timestamp update mechanism.
5. Add migrations.
6. Build Flask models.
7. Add session-based authentication.
8. Build CRUD endpoints.
9. Add tests.
10. Connect the React frontend to the API contract.
