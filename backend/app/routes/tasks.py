from flask import Blueprint, g, jsonify, request
from sqlalchemy import asc, desc, or_
from sqlalchemy.exc import IntegrityError

from ..errors import ApiError, error_response
from ..extensions import db
from ..models import Task
from ..utils import parse_iso_datetime, require_auth, serialize_task

tasks_bp = Blueprint("tasks", __name__)

MAX_DESCRIPTION_LENGTH = 5000
CREATE_ALLOWED_FIELDS = {"title", "description", "due_at", "category"}
UPDATE_ALLOWED_FIELDS = CREATE_ALLOWED_FIELDS


def _task_payload(required_title=False):
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ApiError("VALIDATION_ERROR", "Request body must be a JSON object.", 400)

    if required_title and (not isinstance(data.get("title"), str) or not data["title"].strip()):
        raise ApiError("VALIDATION_ERROR", "Title is required.", 400)

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            raise ApiError("VALIDATION_ERROR", "Title must be a non-empty string.", 400)
        if len(data["title"].strip()) > 255:
            raise ApiError("VALIDATION_ERROR", "Title must not exceed 255 characters.", 400)

    if "description" in data:
        if data["description"] is not None and not isinstance(data["description"], str):
            raise ApiError("VALIDATION_ERROR", "Description must be a string or null.", 400)
        if isinstance(data["description"], str) and len(data["description"]) > MAX_DESCRIPTION_LENGTH:
            raise ApiError("VALIDATION_ERROR", "Description must not exceed 5000 characters.", 400)

    if "category" in data:
        if data["category"] is not None and not isinstance(data["category"], str):
            raise ApiError("VALIDATION_ERROR", "Category must be a string or null.", 400)
        if isinstance(data["category"], str) and len(data["category"].strip()) > 100:
            raise ApiError("VALIDATION_ERROR", "Category must not exceed 100 characters.", 400)

    if "due_at" in data and data["due_at"] is not None:
        due_at = parse_iso_datetime(data["due_at"], "due_at")
        from datetime import datetime, timezone
        if due_at <= datetime.now(timezone.utc):
            raise ApiError("VALIDATION_ERROR", "due_at must be in the future.", 400)

    return data


def _get_task_or_404(task_id):
    task = db.session.scalar(
        db.select(Task).where(
            Task.id == task_id,
            Task.user_id == g.current_user.id,
            Task.deleted_at.is_(None),
        )
    )
    if task is None:
        raise ApiError("RESOURCE_NOT_FOUND", "The requested task was not found.", 404)
    return task


@tasks_bp.get("")
@require_auth
def list_tasks():
    query = db.select(Task).where(
        Task.user_id == g.current_user.id,
        Task.deleted_at.is_(None),
    )

    search = request.args.get("search")
    if search:
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Task.title.ilike(term),
                Task.description.ilike(term),
                Task.category.ilike(term),
            )
        )

    completed = request.args.get("completed")
    if completed is not None:
        if completed.lower() not in ("true", "false"):
            raise ApiError("VALIDATION_ERROR", "completed must be true or false.", 400)
        query = query.where(Task.completed == (completed.lower() == "true"))

    category = request.args.get("category")
    if category:
        query = query.where(Task.category.ilike(category.strip()))

    due_after = request.args.get("due_after")
    if due_after:
        query = query.where(Task.due_at >= parse_iso_datetime(due_after, "due_after"))

    due_before = request.args.get("due_before")
    if due_before:
        query = query.where(Task.due_at <= parse_iso_datetime(due_before, "due_before"))

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError as exc:
        raise ApiError("VALIDATION_ERROR", "page and per_page must be integers.", 400) from exc

    if page < 1 or per_page < 1 or per_page > 100:
        raise ApiError("VALIDATION_ERROR", "page must be >= 1 and per_page must be between 1 and 100.", 400)

    sort = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc").lower()

    sort_columns = {
        "title": Task.title,
        "due_at": Task.due_at,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
    }
    if sort not in sort_columns:
        raise ApiError("VALIDATION_ERROR", "Invalid sort field.", 400)
    if order not in ("asc", "desc"):
        raise ApiError("VALIDATION_ERROR", "order must be asc or desc.", 400)

    column = sort_columns[sort]
    if sort == "due_at":
        query = query.order_by(
            column.is_(None).asc(),
            asc(column) if order == "asc" else desc(column),
        )
    else:
        query = query.order_by(asc(column) if order == "asc" else desc(column))
    query = query.offset((page - 1) * per_page).limit(per_page)

    tasks = db.session.scalars(query).all()

    count_query = db.select(db.func.count()).select_from(Task).where(
        Task.user_id == g.current_user.id,
        Task.deleted_at.is_(None),
    )
    if search:
        term = f"%{search.strip()}%"
        count_query = count_query.where(
            or_(Task.title.ilike(term), Task.description.ilike(term), Task.category.ilike(term))
        )
    if completed is not None:
        count_query = count_query.where(Task.completed == (completed.lower() == "true"))
    if category:
        count_query = count_query.where(Task.category.ilike(category.strip()))
    if due_after:
        count_query = count_query.where(Task.due_at >= parse_iso_datetime(due_after, "due_after"))
    if due_before:
        count_query = count_query.where(Task.due_at <= parse_iso_datetime(due_before, "due_before"))

    total = db.session.scalar(count_query) or 0

    return jsonify({
        "tasks": [serialize_task(task) for task in tasks],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
    }), 200


@tasks_bp.post("")
@require_auth
def create_task():
    data = _task_payload(required_title=True)
    unexpected = set(data) - CREATE_ALLOWED_FIELDS
    if unexpected:
        raise ApiError(
            "VALIDATION_ERROR",
            "Unsupported fields: " + ", ".join(sorted(unexpected)) + ".",
            400,
        )

    task = Task(
        user_id=g.current_user.id,
        title=data["title"].strip(),
        description=data.get("description"),
        completed=False,
        due_at=parse_iso_datetime(data["due_at"], "due_at") if data.get("due_at") else None,
        category=data.get("category").strip() if isinstance(data.get("category"), str) else None,
    )
    db.session.add(task)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint_name == "uq_active_task_title_per_user":
            raise ApiError(
                "TASK_TITLE_ALREADY_EXISTS",
                "An active task with this title already exists.",
                409,
            ) from exc
        raise

    return jsonify({"task": serialize_task(task)}), 201


@tasks_bp.get("/<uuid:task_id>")
@require_auth
def get_task(task_id):
    return jsonify({"task": serialize_task(_get_task_or_404(task_id))}), 200


@tasks_bp.patch("/<uuid:task_id>")
@require_auth
def update_task(task_id):
    task = _get_task_or_404(task_id)
    data = _task_payload()

    if not data:
        raise ApiError("VALIDATION_ERROR", "At least one supported field is required.", 400)

    unexpected = set(data) - UPDATE_ALLOWED_FIELDS
    if unexpected:
        raise ApiError(
            "VALIDATION_ERROR",
            f"Unsupported fields: {', '.join(sorted(unexpected))}.",
            400,
        )

    if "title" in data:
        task.title = data["title"].strip()
    if "description" in data:
        task.description = data["description"]
    if "due_at" in data:
        task.due_at = parse_iso_datetime(data["due_at"], "due_at") if data["due_at"] else None
    if "category" in data:
        task.category = data["category"].strip() if isinstance(data["category"], str) else None

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint_name == "uq_active_task_title_per_user":
            raise ApiError(
                "TASK_TITLE_ALREADY_EXISTS",
                "An active task with this title already exists.",
                409,
            ) from exc
        raise

    return jsonify({"task": serialize_task(task)}), 200


@tasks_bp.delete("/<uuid:task_id>")
@require_auth
def delete_task(task_id):
    task = _get_task_or_404(task_id)
    from datetime import datetime, timezone
    task.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    return "", 204


@tasks_bp.patch("/<uuid:task_id>/complete")
@require_auth
def complete_task(task_id):
    task = _get_task_or_404(task_id)
    data = request.get_json(silent=True) or {}

    if not isinstance(data, dict) or not isinstance(data.get("completed"), bool):
        raise ApiError("VALIDATION_ERROR", "completed must be a boolean.", 400)

    task.completed = data["completed"]
    db.session.commit()

    return jsonify({
        "task": {
            "id": str(task.id),
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat(),
        }
    }), 200


@tasks_bp.errorhandler(ApiError)
def handle_task_error(error):
    return error_response(error.code, error.message, error.status_code)
