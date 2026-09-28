"""Task CRUD routes."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from .auth import require_auth
from .errors import APIError
from .extensions import db
from .models import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

ALLOWED_SORTS = {"created_at", "updated_at", "due_at", "title"}


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


@tasks_bp.get("")
@require_auth
def list_tasks(user):
    page = _positive_int(request.args.get("page", 1), "page")
    per_page = _positive_int(request.args.get("per_page", 20), "per_page")
    if per_page > 100:
        raise APIError(400, "VALIDATION_ERROR", "per_page cannot exceed 100")

    query = Task.query.filter_by(user_id=user.id, deleted_at=None)

    search = request.args.get("search")
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            db.or_(Task.title.ilike(term), Task.description.ilike(term))
        )

    completed = request.args.get("completed")
    if completed is not None:
        if completed not in {"true", "false"}:
            raise APIError(400, "VALIDATION_ERROR", "completed must be true or false")
        query = query.filter(Task.completed.is_(completed == "true"))

    category = request.args.get("category")
    if category:
        query = query.filter(Task.category == category)

    due_before = _parse_datetime(request.args.get("due_before"), "due_before")
    due_after = _parse_datetime(request.args.get("due_after"), "due_after")
    if due_before:
        query = query.filter(Task.due_at <= due_before)
    if due_after:
        query = query.filter(Task.due_at >= due_after)

    sort = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")
    if sort not in ALLOWED_SORTS or order not in {"asc", "desc"}:
        raise APIError(400, "VALIDATION_ERROR", "Invalid sort or order")

    column = getattr(Task, sort)
    query = query.order_by(column.asc() if order == "asc" else column.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "tasks": [serialize_task(task) for task in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        },
    })


@tasks_bp.post("")
@require_auth
def create_task(user):
    data = _json_body()
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise APIError(400, "VALIDATION_ERROR", "Title is required")

    title = title.strip()
    description = data.get("description")
    category = data.get("category")
    due_at = _parse_datetime(data.get("due_at"), "due_at")

    if len(title) > 255:
        raise APIError(400, "VALIDATION_ERROR", "Title cannot exceed 255 characters")
    if description is not None and (not isinstance(description, str) or len(description) > 5000):
        raise APIError(400, "VALIDATION_ERROR", "Description cannot exceed 5000 characters")
    if category is not None and (not isinstance(category, str) or len(category) > 100):
        raise APIError(400, "VALIDATION_ERROR", "Category cannot exceed 100 characters")
    if due_at and due_at <= datetime.now(timezone.utc):
        raise APIError(400, "VALIDATION_ERROR", "Due date must be in the future")
    if Task.query.filter_by(user_id=user.id, title=title, deleted_at=None).first():
        raise APIError(409, "TASK_TITLE_ALREADY_EXISTS", "An active task with this title already exists")

    task = Task(
        user_id=user.id,
        title=title,
        description=description,
        due_at=due_at,
        category=category.strip() if isinstance(category, str) else category,
        completed=False,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(serialize_task(task)), 201


@tasks_bp.get("/<uuid:task_id>")
@require_auth
def get_task(user, task_id):
    task = _get_owned_task(user.id, task_id)
    return jsonify(serialize_task(task))


@tasks_bp.patch("/<uuid:task_id>")
@require_auth
def update_task(user, task_id):
    task = _get_owned_task(user.id, task_id)
    data = _json_body()
    allowed = {"title", "description", "due_at", "category"}

    unknown = set(data) - allowed
    if unknown:
        raise APIError(400, "VALIDATION_ERROR", "Only title, description, due_at, and category may be updated")

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            raise APIError(400, "VALIDATION_ERROR", "Title cannot be empty")
        title = title.strip()
        if len(title) > 255:
            raise APIError(400, "VALIDATION_ERROR", "Title cannot exceed 255 characters")
        duplicate = Task.query.filter(
            Task.user_id == user.id,
            Task.title == title,
            Task.id != task.id,
            Task.deleted_at.is_(None),
        ).first()
        if duplicate:
            raise APIError(409, "TASK_TITLE_ALREADY_EXISTS", "An active task with this title already exists")
        task.title = title

    if "description" in data:
        if data["description"] is not None and (not isinstance(data["description"], str) or len(data["description"]) > 5000):
            raise APIError(400, "VALIDATION_ERROR", "Description cannot exceed 5000 characters")
        task.description = data["description"]

    if "due_at" in data:
        due_at = _parse_datetime(data["due_at"], "due_at")
        if due_at and due_at <= datetime.now(timezone.utc):
            raise APIError(400, "VALIDATION_ERROR", "Due date must be in the future")
        task.due_at = due_at

    if "category" in data:
        category = data["category"]
        if category is not None and (not isinstance(category, str) or len(category) > 100):
            raise APIError(400, "VALIDATION_ERROR", "Category cannot exceed 100 characters")
        task.category = category.strip() if isinstance(category, str) else category

    db.session.commit()
    return jsonify(serialize_task(task))


@tasks_bp.patch("/<uuid:task_id>/complete")
@require_auth
def complete_task(user, task_id):
    task = _get_owned_task(user.id, task_id)
    data = _json_body()
    if set(data) != {"completed"} or not isinstance(data["completed"], bool):
        raise APIError(400, "VALIDATION_ERROR", "completed must be a boolean")

    task.completed = data["completed"]
    db.session.commit()
    return jsonify({
        "id": str(task.id),
        "completed": task.completed,
        "updated_at": task.updated_at.isoformat(),
    })


@tasks_bp.delete("/<uuid:task_id>")
@require_auth
def delete_task(user, task_id):
    task = _get_owned_task(user.id, task_id)
    task.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    return "", 204


def _get_owned_task(user_id, task_id):
    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id,
        deleted_at=None,
    ).first()
    if not task:
        raise APIError(404, "RESOURCE_NOT_FOUND", "Resource not found")
    return task


def _json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise APIError(400, "VALIDATION_ERROR", "Request body must be a JSON object")
    return data


def _positive_int(value, name):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise APIError(400, "VALIDATION_ERROR", f"{name} must be a positive integer")
    if value < 1:
        raise APIError(400, "VALIDATION_ERROR", f"{name} must be a positive integer")
    return value


def _parse_datetime(value, field):
    if value is None:
        return None
    if not isinstance(value, str):
        raise APIError(400, "VALIDATION_ERROR", f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise APIError(400, "VALIDATION_ERROR", f"{field} must be an ISO-8601 timestamp")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
