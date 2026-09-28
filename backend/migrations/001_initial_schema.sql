-- Initial PostgreSQL schema for the HNG 15 Todo List MVP.
-- Safe to apply to a fresh database. The application owns UUID generation,
-- so no PostgreSQL UUID extension is required.

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    fullname VARCHAR(150) NOT NULL,
    password_hash TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ NULL,
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_users_username_lower
    ON users (LOWER(username))
    WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    due_at TIMESTAMPTZ NULL,
    category VARCHAR(100) NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS ix_tasks_user_id ON tasks (user_id);
CREATE INDEX IF NOT EXISTS ix_tasks_due_at ON tasks (due_at);
CREATE INDEX IF NOT EXISTS ix_tasks_category ON tasks (category);
CREATE INDEX IF NOT EXISTS ix_tasks_deleted_at ON tasks (deleted_at);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_task_title_per_user
    ON tasks (user_id, title)
    WHERE deleted_at IS NULL;
