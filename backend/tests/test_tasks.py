import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app import create_app
from app.extensions import db
from app.models import Task


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to run PostgreSQL integration tests.",
)


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_SAMESITE": "Lax",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, username="jerry", email="jerry@example.com"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "strong-password",
            "username": username,
            "fullname": "Jerry Example",
        },
    )


def future(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def create_task(client, title, **fields):
    return client.post("/api/tasks", json={"title": title, **fields})


def test_create_task_sets_owner_and_defaults_completion(client, app):
    assert register(client).status_code == 201

    response = create_task(
        client,
        "Study Flask",
        description="Review blueprints",
        due_at=future(),
        category="School",
    )

    assert response.status_code == 201
    task = response.json["task"]
    assert task["title"] == "Study Flask"
    assert task["description"] == "Review blueprints"
    assert task["completed"] is False
    assert task["category"] == "School"
    assert task["due_at"] is not None

    with app.app_context():
        stored = db.session.get(Task, task["id"])
        assert stored is not None


def test_create_rejects_unknown_fields(client):
    assert register(client).status_code == 201

    response = create_task(client, "Invalid", priority="high")

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_create_rejects_client_owned_user_id(client):
    assert register(client).status_code == 201

    response = create_task(client, "Owned correctly", user_id="00000000-0000-0000-0000-000000000001")

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_create_rejects_invalid_title_and_past_due_date(client):
    assert register(client).status_code == 201

    empty_title = create_task(client, "   ")
    assert empty_title.status_code == 400
    assert empty_title.json["error"]["code"] == "VALIDATION_ERROR"

    past_due = create_task(
        client,
        "Past due",
        due_at=(datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
    )
    assert past_due.status_code == 400
    assert past_due.json["error"]["code"] == "VALIDATION_ERROR"


def test_duplicate_active_title_is_rejected_per_user(client):
    assert register(client).status_code == 201
    assert create_task(client, "Same title").status_code == 201

    response = create_task(client, "Same title")

    assert response.status_code == 409
    assert response.json["error"]["code"] == "TASK_TITLE_ALREADY_EXISTS"


def test_get_task_returns_owned_active_task(client):
    assert register(client).status_code == 201
    created = create_task(client, "Read me")
    task_id = created.json["task"]["id"]

    response = client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json["task"]["id"] == task_id


def test_patch_updates_allowed_fields(client):
    assert register(client).status_code == 201
    created = create_task(client, "Original", category="School")
    task_id = created.json["task"]["id"]

    response = client.patch(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated",
            "description": "Changed",
            "due_at": future(),
            "category": "Work",
        },
    )

    assert response.status_code == 200
    task = response.json["task"]
    assert task["title"] == "Updated"
    assert task["description"] == "Changed"
    assert task["category"] == "Work"
    assert task["due_at"] is not None


def test_patch_rejects_empty_and_unknown_fields(client):
    assert register(client).status_code == 201
    created = create_task(client, "Original")
    task_id = created.json["task"]["id"]

    empty = client.patch(f"/api/tasks/{task_id}", json={})
    assert empty.status_code == 400
    assert empty.json["error"]["code"] == "VALIDATION_ERROR"

    unknown = client.patch(f"/api/tasks/{task_id}", json={"priority": "high"})
    assert unknown.status_code == 400
    assert unknown.json["error"]["code"] == "VALIDATION_ERROR"


def test_patch_cannot_change_completion_or_identity(client):
    assert register(client).status_code == 201
    created = create_task(client, "Original")
    task_id = created.json["task"]["id"]

    response = client.patch(
        f"/api/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_complete_sets_explicit_state_without_toggle(client):
    assert register(client).status_code == 201
    created = create_task(client, "Complete me")
    task_id = created.json["task"]["id"]

    completed = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": True},
    )
    assert completed.status_code == 200
    assert completed.json["task"]["completed"] is True

    uncompleted = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": False},
    )
    assert uncompleted.status_code == 200
    assert uncompleted.json["task"]["completed"] is False


def test_complete_rejects_non_boolean_and_unknown_fields(client):
    assert register(client).status_code == 201
    created = create_task(client, "Complete validation")
    task_id = created.json["task"]["id"]

    invalid = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": "true"},
    )
    assert invalid.status_code == 400
    assert invalid.json["error"]["code"] == "VALIDATION_ERROR"

    unknown = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": True, "priority": "high"},
    )
    assert unknown.status_code == 400
    assert unknown.json["error"]["code"] == "VALIDATION_ERROR"


def test_delete_soft_deletes_and_hides_task(client, app):
    assert register(client).status_code == 201
    created = create_task(client, "Delete me")
    task_id = created.json["task"]["id"]

    response = client.delete(f"/api/tasks/{task_id}")

    assert response.status_code == 204
    assert response.data == b""
    assert client.get(f"/api/tasks/{task_id}").status_code == 404

    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task.deleted_at is not None


def test_deleted_title_can_be_reused(client):
    assert register(client).status_code == 201
    created = create_task(client, "Reusable")
    task_id = created.json["task"]["id"]

    assert client.delete(f"/api/tasks/{task_id}").status_code == 204

    response = create_task(client, "Reusable")
    assert response.status_code == 201


def test_list_search_is_case_insensitive_and_checks_all_text_fields(client):
    assert register(client).status_code == 201
    create_task(client, "Learn Flask", description="BluePrint practice", category="Backend")
    create_task(client, "Read SQL", description="Database notes", category="School")

    response = client.get("/api/tasks?search=BLUEPRINT")

    assert response.status_code == 200
    assert [task["title"] for task in response.json["tasks"]] == ["Learn Flask"]


def test_list_filters_category_case_insensitively(client):
    assert register(client).status_code == 201
    create_task(client, "Backend task", category="Backend")
    create_task(client, "School task", category="School")

    response = client.get("/api/tasks?category=backend")

    assert response.status_code == 200
    assert [task["title"] for task in response.json["tasks"]] == ["Backend task"]


def test_list_filters_completion_and_due_range(client):
    assert register(client).status_code == 201
    create_task(client, "Done", due_at=future(1))
    pending = create_task(client, "Pending", due_at=future(3))
    pending_id = pending.json["task"]["id"]
    assert client.patch(f"/api/tasks/{pending_id}/complete", json={"completed": True}).status_code == 200

    completed = client.get("/api/tasks?completed=true")
    assert completed.status_code == 200
    assert [task["title"] for task in completed.json["tasks"]] == ["Pending"]

    due_range = client.get(f"/api/tasks?due_after={future(0.5)}&due_before={future(2)}")
    assert due_range.status_code == 200
    assert [task["title"] for task in due_range.json["tasks"]] == ["Done"]


def test_list_sorts_due_dates_with_undated_tasks_last(client):
    assert register(client).status_code == 201
    create_task(client, "Undated")
    create_task(client, "Later", due_at=future(3))
    create_task(client, "Soon", due_at=future(1))

    ascending = client.get("/api/tasks?sort=due_at&order=asc")
    assert ascending.status_code == 200
    assert [task["title"] for task in ascending.json["tasks"]] == ["Soon", "Later", "Undated"]

    descending = client.get("/api/tasks?sort=due_at&order=desc")
    assert descending.status_code == 200
    assert [task["title"] for task in descending.json["tasks"]] == ["Later", "Soon", "Undated"]


def test_list_paginates_and_reports_totals(client):
    assert register(client).status_code == 201
    for index in range(5):
        create_task(client, f"Task {index}")

    response = client.get("/api/tasks?page=2&per_page=2")

    assert response.status_code == 200
    assert len(response.json["tasks"]) == 2
    assert response.json["pagination"] == {
        "page": 2,
        "per_page": 2,
        "total": 5,
        "total_pages": 3,
    }


def test_list_rejects_invalid_pagination_sort_and_order(client):
    assert register(client).status_code == 201

    for query in (
        "page=0",
        "per_page=0",
        "per_page=101",
        "page=nope",
        "sort=priority",
        "order=sideways",
        "completed=maybe",
    ):
        response = client.get(f"/api/tasks?{query}")
        assert response.status_code == 400
        assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_task_ownership_isolation_for_list_and_mutations(client, app):
    owner = client
    attacker = app.test_client()

    assert register(owner, "owner", "owner@example.com").status_code == 201
    created = create_task(owner, "Private task")
    task_id = created.json["task"]["id"]

    assert register(attacker, "attacker", "attacker@example.com").status_code == 201

    listed = attacker.get("/api/tasks")
    assert listed.status_code == 200
    assert listed.json["pagination"]["total"] == 0

    for method, path, payload in (
        ("get", f"/api/tasks/{task_id}", None),
        ("patch", f"/api/tasks/{task_id}", {"title": "Hijacked"}),
        ("patch", f"/api/tasks/{task_id}/complete", {"completed": True}),
        ("delete", f"/api/tasks/{task_id}", None),
    ):
        response = (
            getattr(attacker, method)(path, json=payload)
            if payload is not None
            else getattr(attacker, method)(path)
        )
        assert response.status_code == 404
        assert response.json["error"]["code"] == "RESOURCE_NOT_FOUND"

    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task.title == "Private task"
        assert task.completed is False
        assert task.deleted_at is None
