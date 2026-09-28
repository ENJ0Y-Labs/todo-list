from flask import Blueprint, jsonify, request, session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
import re

from ..errors import ApiError, error_response
from ..extensions import db
from ..models import User
from ..utils import require_auth, serialize_user

auth_bp = Blueprint("auth", __name__)


def _registration_data():
    data = request.get_json(silent=True) or {}
    required = ("email", "password", "username", "fullname")

    for field in required:
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ApiError("VALIDATION_ERROR", f"{field} is required.", 400)

    email = data["email"].strip().lower()
    password = data["password"]
    username = data["username"].strip()
    fullname = data["fullname"].strip()

    if len(email) > 255:
        raise ApiError("VALIDATION_ERROR", "Email must not exceed 255 characters.", 400)
    if not re.fullmatch(r"[^@\\s]+@[^@\\s]+\\.[^@\\s]+", email):
        raise ApiError("VALIDATION_ERROR", "Email must be a valid email address.", 400)
    if len(password) < 8:
        raise ApiError("VALIDATION_ERROR", "Password must be at least 8 characters.", 400)
    if len(password) > 128:
        raise ApiError("VALIDATION_ERROR", "Password must not exceed 128 characters.", 400)
    if len(username) > 100:
        raise ApiError("VALIDATION_ERROR", "Username must not exceed 100 characters.", 400)
    if len(fullname) > 150:
        raise ApiError("VALIDATION_ERROR", "Full name must not exceed 150 characters.", 400)

    return email, password, username, fullname


@auth_bp.post("/register")
def register():
    email, password, username, fullname = _registration_data()

    existing_email = db.session.scalar(
        db.select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    if existing_email:
        raise ApiError(
            "EMAIL_ALREADY_REGISTERED",
            "This email is already registered.",
            409,
        )

    existing_username = db.session.scalar(
        db.select(User).where(
            func.lower(User.username) == username.lower(),
            User.deleted_at.is_(None),
        )
    )
    if existing_username:
        raise ApiError(
            "USERNAME_ALREADY_REGISTERED",
            "This username is already registered.",
            409,
        )

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        username=username,
        fullname=fullname,
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        constraint_name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)

        if constraint_name == "uq_users_email":
            raise ApiError(
                "EMAIL_ALREADY_REGISTERED",
                "This email is already registered.",
                409,
            ) from exc

        if constraint_name == "uq_active_users_username_lower":
            raise ApiError(
                "USERNAME_ALREADY_REGISTERED",
                "This username is already registered.",
                409,
            ) from exc

        raise

    session.clear()
    session["user_id"] = str(user.id)

    return jsonify({
        "user": serialize_user(user),
        "authenticated": True,
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip() or not isinstance(password, str) or not password:
        raise ApiError("VALIDATION_ERROR", "Username and password are required.", 400)

    user = db.session.scalar(
        db.select(User).where(
            func.lower(User.username) == username.strip().lower(),
            User.deleted_at.is_(None),
        )
    )

    if user is None or not check_password_hash(user.password_hash, password):
        raise ApiError(
            "INVALID_CREDENTIALS",
            "Invalid username or password.",
            401,
        )

    if user.status != "active":
        raise ApiError("ACCOUNT_SUSPENDED", "This account is suspended.", 403)

    session.clear()
    session["user_id"] = str(user.id)

    return jsonify({
        "user": serialize_user(user),
        "authenticated": True,
    }), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return "", 204


@auth_bp.get("/me")
@require_auth
def me():
    return jsonify({
        "user": session_user(),
        "authenticated": True,
    }), 200


def session_user():
    from flask import g
    return serialize_user(g.current_user)


@auth_bp.errorhandler(ApiError)
def handle_auth_error(error):
    return error_response(error.code, error.message, error.status_code)
