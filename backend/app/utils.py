from datetime import datetime, timezone
from functools import wraps

from flask import g, session

from .errors import ApiError
from .extensions import db
from .models import User


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            raise ApiError(
                "AUTHENTICATION_REQUIRED",
                "Authentication is required.",
                401,
            )

        user = db.session.get(User, user_id)
        if user is None or user.deleted_at is not None:
            session.clear()
            raise ApiError(
                "AUTHENTICATION_REQUIRED",
                "Authentication is required.",
                401,
            )

        if user.status != "active":
            raise ApiError(
                "ACCOUNT_SUSPENDED",
                "This account is suspended.",
                403,
            )

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def parse_iso_datetime(value, field_name="datetime"):
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ApiError("VALIDATION_ERROR", f"{field_name} must be a valid ISO 8601 datetime.", 400)

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApiError("VALIDATION_ERROR", f"{field_name} must be a valid ISO 8601 datetime.", 400) from exc

    if parsed.tzinfo is None:
        raise ApiError("VALIDATION_ERROR", f"{field_name} must include a timezone.", 400)

    return parsed.astimezone(timezone.utc)


def serialize_user(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "fullname": user.fullname,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }


def serialize_task(task):
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "due_at": task.due_at.isoformat() if task.due_at else None,
        "category": task.category,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
