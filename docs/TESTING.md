# Testing

## Backend command

From backend:

python -m pytest -q

The backend tests require PostgreSQL and TEST_DATABASE_URL. A missing TEST_DATABASE_URL is a test failure, not a skipped green run.

The fixture applies backend/migrations/001_initial_schema.sql to a throwaway PostgreSQL database before each test and uses the same server-side CacheLib session backend family as the application.

## Backend test areas

The current suite covers:
- registration and password hashing
- lowercase email normalization
- case-insensitive username handling
- duplicate email and username handling
- suspended-account rejection
- immediate authentication after registration
- logout and current-user lookup
- protected task endpoints
- cross-user task isolation
- client-supplied user_id ownership protection
- task CRUD
- completion and incompletion
- soft deletion and title reuse
- duplicate active task titles
- search, category filtering, completion filtering, pagination, and sorting
- input allowlists and invalid pagination/filter values
- due-date filtering and ordering

The suite also provisions the actual migration rather than using SQLAlchemy create_all, so a missing schema cannot be hidden by the test fixture.

## Frontend command

From frontend:

npm test

Production build check:

npm run build

## Test philosophy

For each feature:
1. Test the happy path.
2. Test invalid input.
3. Test authorization where relevant.
4. Test the response contract.
5. Test important boundaries.
6. Run the relevant suite.
7. Review the diff.
8. Update documentation when behavior changes.

A green test suite is necessary, not sufficient. The implementation and contract still need review.

## CI

GitHub Actions runs the PostgreSQL migration, backend tests, frontend tests, and frontend production build on pushes and pull requests targeting main.

## Warnings

Dependency warnings should be treated as maintenance work, not hidden by changing test configuration.
