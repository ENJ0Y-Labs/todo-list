import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import Task, User


def register(client, username="jerry", email="jerry@example.com", password="strong-password"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "username": username,
            "fullname": "Jerry Example",
        },
    )


def test_register_creates_authenticated_session_and_hashes_password(client, app):
    response = register(client, email="JERRY@Example.COM")

    assert response.status_code == 201
    assert response.json["authenticated"] is True
    assert response.json["user"]["username"] == "jerry"
    assert response.json["user"]["email"] == "jerry@example.com"
    assert "password_hash" not in response.json["user"]
    assert "session" not in response.json["user"]

    set_cookie = response.headers.get("Set-Cookie")
    assert set_cookie is not None
    assert "HttpOnly" in set_cookie

    with app.app_context():
        user = db.session.scalar(select(User).where(User.username == "jerry"))
        assert user is not None
        assert user.email == "jerry@example.com"
        assert user.password_hash != "strong-password"
        assert user.password_hash.startswith(("scrypt:", "pbkdf2:"))


def test_duplicate_email_returns_distinct_conflict(client):
    assert register(client).status_code == 201

    response = register(
        client,
        username="other",
        email="JERRY@example.com",
    )

    assert response.status_code == 409
    assert response.json["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_duplicate_username_is_case_insensitive(client):
    assert register(client).status_code == 201

    response = register(
        client,
        username="JERRY",
        email="other@example.com",
    )

    assert response.status_code == 409
    assert response.json["error"]["code"] == "USERNAME_ALREADY_REGISTERED"


def test_login_uses_username_case_insensitively(client):
    assert register(client).status_code == 201
    assert client.post("/api/auth/logout").status_code == 204

    response = client.post(
        "/api/auth/login",
        json={"username": "JERRY", "password": "strong-password"},
    )

    assert response.status_code == 200
    assert response.json["authenticated"] is True
    assert response.json["user"]["username"] == "jerry"
    assert response.json["user"]["email"] == "jerry@example.com"
    assert "password_hash" not in response.json["user"]


def test_login_rejects_invalid_credentials(client):
    assert register(client).status_code == 201
    assert client.post("/api/auth/logout").status_code == 204

    response = client.post(
        "/api/auth/login",
        json={"username": "jerry", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_authentication(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/api/tasks", None),
        ("post", "/api/tasks", {"title": "Protected"}),
        ("get", "/api/tasks/00000000-0000-0000-0000-000000000000", None),
        ("patch", "/api/tasks/00000000-0000-0000-0000-000000000000", {"title": "Changed"}),
        ("patch", "/api/tasks/00000000-0000-0000-0000-000000000000/complete", {"completed": True}),
        ("delete", "/api/tasks/00000000-0000-0000-0000-000000000000", None),
    ],
)
def test_protected_task_endpoints_require_authentication(client, method, path, payload):
    response = getattr(client, method)(path, json=payload) if payload is not None else getattr(client, method)(path)

    assert response.status_code == 401
    assert response.json["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_logout_clears_session(client):
    assert register(client).status_code == 201

    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_suspended_account_cannot_use_protected_endpoints(client, app):
    assert register(client).status_code == 201

    with app.app_context():
        user = db.session.scalar(select(User).where(User.username == "jerry"))
        user.status = "suspended"
        db.session.commit()

    response = client.get("/api/auth/me")

    assert response.status_code == 403
    assert response.json["error"]["code"] == "ACCOUNT_SUSPENDED"


def test_cross_user_task_access_is_hidden(client, app):
    owner = client
    attacker = app.test_client()

    assert register(owner, username="owner", email="owner@example.com").status_code == 201
    created = owner.post("/api/tasks", json={"title": "Private task"})
    assert created.status_code == 201
    task_id = created.json["task"]["id"]

    assert register(attacker, username="attacker", email="attacker@example.com").status_code == 201
    attacker_list = attacker.get("/api/tasks")
    assert attacker_list.status_code == 200
    assert attacker_list.json["tasks"] == []

    for method, path, payload in (
        ("get", f"/api/tasks/{task_id}", None),
        ("patch", f"/api/tasks/{task_id}", {"title": "Hijacked"}),
        ("delete", f"/api/tasks/{task_id}", None),
        ("patch", f"/api/tasks/{task_id}/complete", {"completed": True}),
    ):
        response = getattr(attacker, method)(path, json=payload) if payload is not None else getattr(attacker, method)(path)
        assert response.status_code == 404
        assert response.json["error"]["code"] == "RESOURCE_NOT_FOUND"

    with app.app_context():
        task = db.session.scalar(select(Task).where(Task.id == task_id))
        assert task.title == "Private task"
        assert task.completed is False
        assert task.deleted_at is None


def test_create_task_ignores_client_supplied_user_id(client, app):
    assert register(client).status_code == 201

    with app.app_context():
        other = User(
            email="other@example.com",
            username="other",
            fullname="Other User",
            password_hash="not-used",
        )
        db.session.add(other)
        db.session.commit()
        other_id = str(other.id)

    response = client.post(
        "/api/tasks",
        json={"title": "Owned by me", "user_id": other_id},
    )

    assert response.status_code == 201
    task_id = response.json["task"]["id"]

    with app.app_context():
        task = db.session.scalar(select(Task).where(Task.id == task_id))
        current_user = db.session.scalar(select(User).where(User.username == "jerry"))
        assert str(task.user_id) == str(current_user.id)
