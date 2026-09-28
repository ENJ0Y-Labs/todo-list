# Testing

## Backend command

From backend:

python -m pytest -q

The backend tests require PostgreSQL and TEST_DATABASE_URL. They intentionally do not fall back to SQLite.

## Backend test areas

### Authentication
- Registration success and validation.
- Password length.
- Lowercase email normalization.
- Case-insensitive username handling.
- Duplicate email and username handling.
- Suspended-account rejection.
- Immediate authentication after registration.
- Logout.
- Current-user lookup.
- No password-hash exposure.

### Task validation
- Required title.
- Title length.
- Description length.
- Category length.
- Future due dates.
- Unknown request fields.
- Completion separation from normal task updates.
- Boolean completion validation.

### Ownership
- Users list only their own tasks.
- Users cannot read another user's task.
- Users cannot update another user's task.
- Users cannot complete another user's task.
- Users cannot delete another user's task.
- Client-supplied user_id cannot change task ownership.

### Task behavior
- Creation returns 201.
- Pagination metadata.
- Search.
- Completion filtering.
- Case-insensitive category filtering.
- Due-date filtering.
- Sorting.
- Null due dates after dated tasks.
- Duplicate active task titles per user.
- Soft deletion.

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

GitHub Actions results should be treated as authoritative for the exact commit tested.

Record actual results. Do not claim a test passed without running it.

## Warnings

The backend may currently emit Flask-Session deprecation warnings related to its filesystem session configuration. These warnings do not fail pytest but should be addressed before deprecated APIs are removed by dependencies.
