# Project Documentation

This directory is the source of truth for project-level documentation.

## Documents

- API_CONTRACT.md: HTTP endpoints, request and response formats, validation, authentication, task behavior, and errors.
- DATABASE_DESIGN.md: PostgreSQL schema, relationships, constraints, indexes, and deferred data-model features.
- ARCHITECTURE.md: system architecture, responsibilities, request flow, authentication flow, and ownership boundaries.
- FRONTEND.md: React structure, routing, state management, UI behavior, and frontend conventions.
- TESTING.md: backend and frontend test strategy, commands, and quality expectations.
- DEPLOYMENT.md: local setup, environment configuration, production deployment, and session cookies.
- PRODUCT_SCOPE.md: MVP scope, exclusions, assumptions, and future work.

AGENTS.md contains repository engineering rules and must remain unchanged.

## Stack

React, React Router, Vite, Python, Flask, SQLAlchemy, PostgreSQL, Supabase-compatible PostgreSQL hosting, server-side sessions, HTTP-only cookies, REST and JSON.

## Current MVP

The application supports multi-user authentication and per-user task management. Tasks support CRUD, explicit completion state, search, filtering, sorting, pagination, due dates, categories, and soft deletion.

Deferred features include priority, email verification, password reset, teams, assignment, advanced roles, and audit history.
