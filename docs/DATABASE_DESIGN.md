# Database Design

## MVP Database Decisions

- PostgreSQL
- UUID primary keys
- TIMESTAMPTZ for timestamps
- Singular entity/table naming
- Database-level foreign-key and integrity constraints
- User and Task are the only MVP entities

## User

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| email | VARCHAR(255) | Required, unique, normalized to lowercase |
| username | VARCHAR(100) | Required |
| fullname | VARCHAR(150) | Required |
| password_hash | TEXT | Required; only the hash is stored |
| status | VARCHAR(20) | active or suspended |
| created_at | TIMESTAMPTZ | Required |
| updated_at | TIMESTAMPTZ | Required |
| deleted_at | TIMESTAMPTZ | Nullable; soft deletion |

Email verification is deferred until after the MVP.

## Task

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Required foreign key to User |
| title | VARCHAR(255) | Required |
| description | TEXT | Nullable |
| completed | BOOLEAN | Required, defaults to false |
| due_at | TIMESTAMPTZ | Nullable; API rejects past values |
| category | VARCHAR(100) | Nullable |
| created_at | TIMESTAMPTZ | Required |
| updated_at | TIMESTAMPTZ | Required |
| deleted_at | TIMESTAMPTZ | Nullable; soft deletion |

Priority is intentionally excluded from the MVP.

## Relationship

One User owns many Tasks.

User 1 -------- * Task

The tasks.user_id foreign key is NOT NULL and uses ON DELETE CASCADE.

## Integrity rules

### User email

email UNIQUE NOT NULL

Application logic normalizes emails to lowercase before persistence.

### Task ownership

user_id UUID NOT NULL
FOREIGN KEY -> users.id
ON DELETE CASCADE

### Task completion

completed BOOLEAN NOT NULL DEFAULT FALSE

### Task title

title VARCHAR(255) NOT NULL

Active tasks belonging to the same user cannot have duplicate titles. PostgreSQL should enforce this with a partial unique index over (user_id, title) where deleted_at IS NULL.

### Due date

due_at TIMESTAMPTZ NULL

The API rejects a due timestamp in the past.

### Soft deletion

Both Users and Tasks support deleted_at TIMESTAMPTZ NULL.

Normal application queries exclude records where deleted_at IS NOT NULL.

## Timestamps

All entities use created_at, updated_at, and deleted_at where applicable.

The ORM updates updated_at when a record changes.

## Indexing

Indexes support:

- User email lookup
- Tasks by user
- Active tasks by user
- Due-date filtering/sorting
- Category filtering
- Soft-deletion filtering

## Deferred features

- Email verification
- Password reset
- Task priority
- Separate Category table
- Team members/assignees
- Task assignment
- Advanced roles/permissions
- Audit/event history

## Implementation order

1. Finalize PostgreSQL schema.
2. Add UUID generation.
3. Add constraints and indexes.
4. Add timestamp update mechanism.
5. Create migration.
6. Build Flask models against the schema.
7. Add authentication.
8. Build CRUD endpoints.
9. Add automated tests.
