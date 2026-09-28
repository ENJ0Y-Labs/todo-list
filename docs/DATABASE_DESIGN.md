# Database Design

## MVP Database Decisions

This document defines the database model before CRUD implementation.

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
| description | TEXT | Nullable |
| completed | BOOLEAN | Required, defaults to `false` |
| due_at | TIMESTAMPTZ | Nullable |
| category | VARCHAR(100) | Nullable |
| created_at | TIMESTAMPTZ | Required |
| updated_at | TIMESTAMPTZ | Required |
| deleted_at | TIMESTAMPTZ | Nullable; soft deletion |

Priority is intentionally excluded from the MVP. It can be introduced later through a migration when team/task-assignment requirements justify it.

Category remains a simple field on Task for the MVP rather than a separate Category entity.

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

Application logic normalizes emails to lowercase before persistence.

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

Because Tasks use soft deletion, the eventual PostgreSQL uniqueness constraint should enforce uniqueness only for active records, rather than preventing a restored/recreated title because of a deleted record.

### Due date

```
due_at TIMESTAMPTZ NULL
```

The due date is optional. Application validation should reject a due timestamp in the past.

The database stores the timestamp; the API/frontend decides whether the user supplied a date only or a date and time.

### Soft deletion

Both Users and Tasks support soft deletion:

```
deleted_at TIMESTAMPTZ NULL
```

Normal application queries should exclude records where `deleted_at IS NOT NULL`.

Deleted Tasks may be restored during the retention period. A later cleanup process may permanently purge them.

## Timestamps

All entities use:

- `created_at`: creation timestamp
- `updated_at`: last modification timestamp
- `deleted_at`: nullable soft-deletion timestamp where applicable

The implementation should ensure `updated_at` changes when a record is updated.

## Indexing

Initial indexes should support expected MVP access patterns:

- User email lookup
- Tasks by user
- Active tasks by user
- Due-date filtering/sorting
- Category filtering

Indexes should be added deliberately rather than indiscriminately.

## Deferred Features

These are intentionally outside the initial database model:

- Email verification
- Password reset tokens
- Task priority
- Separate Category table
- Team members/assignees
- Task assignment
- Advanced roles/permissions
- Audit/event history

These should be introduced through migrations when the product requirements justify them.

## Implementation Order

1. Finalize PostgreSQL schema.
2. Add UUID generation.
3. Add constraints and indexes.
4. Add timestamp update mechanism.
5. Create migration.
6. Build Flask models against the schema.
7. Add authentication.
8. Build CRUD endpoints.
9. Add tests.
