"""Authentication routes and helpers."""

from functools import wraps

import bcrypt
from flask import Blueprint, jsonify, session

from .errors import APIError
from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def normalize_email(email):
    return email.strip().lower()


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


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            raise APIError(401, "AUTHENTICATION_REQUIRED", "Authentication is required")

        user = db.session.get(User, user_id)
        if not user or user.deleted_at is not None:
            session.clear()
            raise APIError(401, "AUTHENTICATION_REQUIRED", "Authentication is required")
        if user.status != "active":
            session.clear()
            raise APIError(403, "ACCOUNT_SUSPENDED", "Account is suspended")

        return view(user, *args, **kwargs)

    return wrapped


@auth_bp.post("/register")
def register():
    data = _json_body()
    required = ("email", "password", "username", "fullname")
    _require_fields(data, required)

    email = normalize_email(data["email"])
    username = data["username"].strip()
    fullname = data["fullname"].strip()
    password = data["password"]

    if not email or not username or not fullname or not password:
        raise APIError(400, "VALIDATION_ERROR", "Required fields cannot be empty")
    if len(password) < 8:
        raise APIError(400, "VALIDATION_ERROR", "Password must be at least 8 characters")
    if len(username) > 100 or len(fullname) > 255:
        raise APIError(400, "VALIDATION_ERROR", "Username or fullname is too long")

    if db.session.query(User).filter_by(email=email, deleted_at=None).first():
        raise APIError(409, "EMAIL_ALREADY_REGISTERED", "Email is already registered")
    if db.session.query(User).filter_by(username=username, deleted_at=None).first():
        raise APIError(409, "USERNAME_ALREADY_REGISTERED", "Username is already registered")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(
        email=email,
        password_hash=password_hash,
        username=username,
        fullname=fullname,
    )
    db.session.add(user)
    db.session.commit()

    session.clear()
    session["user_id"] = str(user.id)

    return jsonify({"user": serialize_user(user)}), 201


@auth_bp.post("/login")
def login():
    data = _json_body()
    _require_fields(data, ("email", "password"))

    email = normalize_email(data["email"])
    user = db.session.query(User).filter_by(email=email, deleted_at=None).first()

    if not user or not bcrypt.checkpw(data["password"].encode(), user.password_hash.encode()):
        raise APIError(401, "INVALID_CREDENTIALS", "Invalid email or password")
    if user.status != "active":
        raise APIError(403, "ACCOUNT_SUSPENDED", "Account is suspended")

    session.clear()
    session["user_id"] = str(user.id)
    return jsonify({"user": serialize_user(user)})


@auth_bp.post("/logout")
@require_auth
def logout(_user):
    session.clear()
    return "", 204


@auth_bp.get("/me")
@require_auth
def me(user):
    return jsonify({"user": serialize_user(user)})


def _json_body():
    from flask import request

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise APIError(400, "VALIDATION_ERROR", "Request body must be a JSON object")
    return data


def _require_fields(data, fields):
    missing = [field for field in fields if field not in data]
    if missing:
        raise APIError(400, "VALIDATION_ERROR", f"Missing required field(s): {', '.join(missing)}")
