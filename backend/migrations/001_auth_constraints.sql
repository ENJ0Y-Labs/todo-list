-- Authentication constraints for the existing PostgreSQL users table.
-- Run this migration against an existing database before deploying the
-- username-login version of the API.

ALTER TABLE users
    DROP CONSTRAINT IF EXISTS users_email_key;

ALTER TABLE users
    ADD CONSTRAINT uq_users_email UNIQUE (email);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_users_username_lower
    ON users (LOWER(username))
    WHERE deleted_at IS NULL;
