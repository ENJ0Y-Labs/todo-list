# Frontend

## Stack

- React 19
- React Router 7
- Vite
- JavaScript
- Plain CSS
- Font Awesome
- Vitest
- React Testing Library

The MVP intentionally does not use Tailwind, CSS modules, Redux, React Query, or another state-management/data-fetching library.

## Structure

frontend/src/App.jsx
frontend/src/main.jsx
frontend/src/global.css
frontend/src/context/AuthContext.jsx
frontend/src/pages/Login.jsx
frontend/src/pages/Register.jsx
frontend/src/pages/Dashboard.jsx
frontend/src/services/api.js
frontend/src/test/setup.js

## Routes

| Route | Access | Behavior |
|---|---|---|
| / | Any | Redirect to dashboard, then authentication guard redirects unauthenticated users to login |
| /login | Public | Login screen; authenticated users go to dashboard |
| /register | Public | Registration screen; authenticated users go to dashboard |
| /dashboard | Protected | Main task-management screen |
| unknown | Any | Redirect to / |

## Authentication state

AuthContext owns user, checkingAuth, login, register, and logout.

The session ID is never stored in React state. The browser manages the HTTP-only cookie.

## API service

All frontend HTTP communication is centralized in services/api.js.

Supported operations:
- register
- login
- logout
- current user
- list tasks
- create task
- get task
- update task
- delete task
- set completion state

Every request sends credentials: include.

## Registration

Fields:
- First name
- Last name
- Email
- Username
- Password
- Confirm password

First and last name are combined into the backend fullname field.

Password mismatch is rejected before submission.

## Login

Fields:
- Username
- Password

The MVP has no remember-me or forgot-password UI.

## Dashboard

The dashboard contains:
- Application header.
- Current user display.
- Logout.
- Total, completed, and pending summaries.
- Search.
- Completion filter.
- Category filter.
- Due-date range filters.
- Sort field and order.
- Create-task action.
- Paginated task list.

Each task exposes completion, title, description, category, due date, edit, and delete controls.

## Task creation

Creation uses a modal with title, description, category, and optional due date/time.

Only title is required by the API.

The category UI provides predefined categories and an Other option for custom categories.

## Editing

Task content is edited inline.

Editable fields:
- title
- description
- category
- due date/time

Completion remains a separate operation.

## Completion

Completion sends an explicit boolean to the completion endpoint.

The dashboard removes a newly completed task immediately from the visible list and refreshes the data.

## Deletion

Deletion asks for confirmation before calling the API. The backend soft-deletes the record.

## Query controls

The dashboard supports:
- page
- per_page
- search
- completed
- category
- due_after
- due_before
- sort
- order

The frontend uses per_page=20 and provides previous/next pagination.

Search is debounced when typing.

## Loading and errors

Loading uses a spinner. API errors are shown inline and through toast notifications where appropriate.

Known backend error codes receive friendly frontend messages. Unknown errors use the backend message.

## Styling

All styling is in frontend/src/global.css.

The design is dark mode only, premium and restrained, desktop-first, and responsive.

Font Awesome is loaded from the CDN stylesheet in frontend/index.html.

## Environment

frontend/.env should contain:

VITE_API_BASE_URL=http://localhost:5000/api

Vite environment variables are public to the browser. Never put secrets in VITE_ variables.

## Commands

cd frontend
npm install
npm run dev
npm run build
npm test

Development uses Vite on port 5173 by default.
