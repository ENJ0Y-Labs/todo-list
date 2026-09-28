"""Database models for the Todo API."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint

from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    fullname = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    tasks = db.relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended')", name="ck_users_status"),
    )


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(
        db.Uuid(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    due_at = db.Column(db.DateTime(timezone=True), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", back_populates="tasks")

    __table_args__ = (
        db.Index(
            "uq_tasks_active_user_title",
            "user_id",
            "title",
            unique=True,
            postgresql_where=db.text("deleted_at IS NULL"),
        ),
        db.Index("ix_tasks_active_user", "user_id", "deleted_at"),
        db.Index("ix_tasks_due_at", "due_at"),
        db.Index("ix_tasks_category", "category"),
    )
