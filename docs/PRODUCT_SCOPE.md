# Product Scope

## Product

A clean, multi-user Todo application for the HNG 15 Internship and a foundation for a future team task-management product.

## MVP goal

Provide reliable personal task management with secure authentication and strict task ownership.

## Included

### Authentication
- Registration.
- Immediate authentication after registration.
- Username/password login.
- Logout.
- Current-user lookup.
- Case-insensitive username matching.
- Lowercase email normalization.
- Password hashing.
- Active/suspended status.

### Tasks
- Create.
- Read one.
- List.
- Update.
- Soft delete.
- Explicit completion/incompletion.
- Search.
- Completion filtering.
- Category filtering.
- Due-date filtering.
- Sorting.
- Pagination.
- Per-user ownership isolation.

### Task fields

title, description, completed, due_at, category, created_at, updated_at, deleted_at.

## Frontend

- React.
- Login and registration pages.
- Protected dashboard.
- Dark mode only.
- Responsive layout.
- Create-task modal.
- Inline editing.
- Delete confirmation.
- Loading spinner.
- Inline errors and toast notifications.
- Pagination.
- Search, filter, and sort controls.

## Deferred

- Email verification.
- Password reset.
- Task priority.
- Separate category table.
- Team members.
- Task assignment.
- Advanced roles and permissions.
- Audit/event history.
- Real-time collaboration.
- Notifications.
- Attachments.
- Recurring tasks.

## Product assumptions

1. A task belongs to exactly one user.
2. Users manage their own tasks in the MVP.
3. Authentication uses server-side sessions.
4. Completion is separate from content editing.
5. Deleted tasks use soft deletion.
6. Active task titles are unique per user.
7. Due dates are optional but cannot be in the past.
8. Categories are text values, not a separate entity.
9. PostgreSQL is required.
10. Backend authorization is authoritative.

## Non-goals

The MVP is not a team project-management suite, social task platform, notification system, calendar replacement, role-management system, or native mobile application.

## Change control

Before adding a feature:
1. Define the user problem.
2. Confirm MVP scope.
3. Identify API, database, and UI impact.
4. Update documentation.
5. Add or update tests.
6. Implement in a focused branch and commit.
7. Review the diff.

Do not silently change an API or database contract.
