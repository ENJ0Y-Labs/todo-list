from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import Task


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


def future(hours=24):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def test_task_crud_lifecycle(client, app):
    assert register(client).status_code == 201

    created = client.post(
        "/api/tasks",
        json={
            "title": "Study Flask",
            "description": "Review blueprints",
            "due_at": future(),
            "category": "School",
        },
    )
    assert created.status_code == 201
    task = created.json["task"]
    task_id = task["id"]
    assert task["completed"] is False
    assert task["description"] == "Review blueprints"
    assert task["category"] == "School"
    assert task["due_at"] is not None

    fetched = client.get(f"/api/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json["task"]["title"] == "Study Flask"

    updated = client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "Study Flask API", "category": "Backend"},
    )
    assert updated.status_code == 200
    assert updated.json["task"]["title"] == "Study Flask API"
    assert updated.json["task"]["category"] == "Backend"
    assert updated.json["task"]["completed"] is False

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

    deleted = client.delete(f"/api/tasks/{task_id}")
    assert deleted.status_code == 204

    assert client.get(f"/api/tasks/{task_id}").status_code == 404
    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert listed.json["tasks"] == []

    with app.app_context():
        stored = db.session.get(Task, task_id)
        assert stored.deleted_at is not None


def test_create_rejects_unknown_fields(client):
    assert register(client).status_code == 201

    response = client.post(
        "/api/tasks",
        json={"title": "Valid title", "priority": "high"},
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_create_always_sets_completed_false(client):
    assert register(client).status_code == 201

    response = client.post(
        "/api/tasks",
        json={"title": "Do not start completed", "completed": True},
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_patch_empty_body_is_rejected(client):
    assert register(client).status_code == 201
    created = client.post("/api/tasks", json={"title": "Patch me"})
    task_id = created.json["task"]["id"]

    response = client.patch(f"/api/tasks/{task_id}", json={})

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_completion_requires_boolean_and_does_not_toggle(client):
    assert register(client).status_code == 201
    created = client.post("/api/tasks", json={"title": "Complete me"})
    task_id = created.json["task"]["id"]

    invalid = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": "true"},
    )
    assert invalid.status_code == 400

    first = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": True},
    )
    second = client.patch(
        f"/api/tasks/{task_id}/complete",
        json={"completed": True},
    )
    assert first.json["task"]["completed"] is True
    assert second.json["task"]["completed"] is True


def test_duplicate_active_task_title_returns_conflict(client):
    assert register(client).status_code == 201
    assert client.post("/api/tasks", json={"title": "Same title"}).status_code == 201

    response = client.post("/api/tasks", json={"title": "Same title"})

    assert response.status_code == 409
    assert response.json["error"]["code"] == "TASK_TITLE_ALREADY_EXISTS"


def test_deleted_task_title_can_be_reused(client):
    assert register(client).status_code == 201
    first = client.post("/api/tasks", json={"title": "Reusable title"})
    task_id = first.json["task"]["id"]
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204

    second = client.post("/api/tasks", json={"title": "Reusable title"})

    assert second.status_code == 201


def test_search_matches_title_description_and_category_case_insensitively(client):
    assert register(client).status_code == 201
    client.post(
        "/api/tasks",
        json={"title": "Learn Flask", "description": "REST API practice", "category": "Backend"},
    )
    client.post(
        "/api/tasks",
        json={"title": "Buy food", "description": "Groceries", "category": "Home"},
    )

    for term in ("flask", "REST", "backend"):
        response = client.get("/api/tasks", query_string={"search": term})
        assert response.status_code == 200
        assert len(response.json["tasks"]) == 1
        assert response.json["tasks"][0]["title"] == "Learn Flask"


def test_category_filter_is_case_insensitive(client):
    assert register(client).status_code == 201
    client.post("/api/tasks", json={"title": "One", "category": "School"})
    client.post("/api/tasks", json={"title": "Two", "category": "Work"})

    response = client.get("/api/tasks", query_string={"category": "sChOoL"})

    assert response.status_code == 200
    assert [task["title"] for task in response.json["tasks"]] == ["One"]


def test_completion_filter_and_pagination(client):
    assert register(client).status_code == 201
    for index in range(3):
        response = client.post("/api/tasks", json={"title": f"Task {index}"})
        assert response.status_code == 201
        if index == 1:
            task_id = response.json["task"]["id"]
            assert client.patch(
                f"/api/tasks/{task_id}/complete",
                json={"completed": True},
            ).status_code == 200

    completed = client.get(
        "/api/tasks",
        query_string={"completed": "true", "page": 1, "per_page": 1},
    )

    assert completed.status_code == 200
    assert len(completed.json["tasks"]) == 1
    assert completed.json["pagination"] == {
        "page": 1,
        "per_page": 1,
        "total": 1,
        "total_pages": 1,
    }


def test_pagination_splits_results_and_reports_total(client):
    assert register(client).status_code == 201
    for index in range(5):
        assert client.post("/api/tasks", json={"title": f"Task {index}"}).status_code == 201

    first = client.get("/api/tasks", query_string={"page": 1, "per_page": 2, "sort": "title", "order": "asc"})
    second = client.get("/api/tasks", query_string={"page": 2, "per_page": 2, "sort": "title", "order": "asc"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert [task["title"] for task in first.json["tasks"]] == ["Task 0", "Task 1"]
    assert [task["title"] for task in second.json["tasks"]] == ["Task 2", "Task 3"]
    assert first.json["pagination"]["total"] == 5
    assert first.json["pagination"]["total_pages"] == 3
    assert second.json["pagination"]["page"] == 2


def test_filter_and_pagination_validation(client):
    assert register(client).status_code == 201

    cases = [
        {"completed": "maybe"},
        {"page": "zero"},
        {"page": 0},
        {"per_page": 101},
        {"sort": "priority"},
        {"order": "sideways"},
    ]

    for query_string in cases:
        response = client.get("/api/tasks", query_string=query_string)
        assert response.status_code == 400
        assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_due_date_filters_and_sort_keep_undated_last(client):
    assert register(client).status_code == 201
    client.post("/api/tasks", json={"title": "Undated"})
    client.post(
        "/api/tasks",
        json={"title": "Later", "due_at": future(48)},
    )
    client.post(
        "/api/tasks",
        json={"title": "Soon", "due_at": future(24)},
    )

    response = client.get(
        "/api/tasks",
        query_string={"sort": "due_at", "order": "asc"},
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json["tasks"]] == [
        "Soon",
        "Later",
        "Undated",
    ]

    filtered = client.get(
        "/api/tasks",
        query_string={
            "due_after": (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat(),
            "due_before": (datetime.now(timezone.utc) + timedelta(hours=36)).isoformat(),
        },
    )

    assert filtered.status_code == 200
    assert [task["title"] for task in filtered.json["tasks"]] == ["Soon"]


def test_task_title_uniqueness_is_scoped_to_user(client, app):
    assert register(client, username="owner", email="owner@example.com").status_code == 201
    assert client.post("/api/tasks", json={"title": "Shared title"}).status_code == 201

    other = app.test_client()
    assert register(other, username="other", email="other@example.com").status_code == 201

    response = other.post("/api/tasks", json={"title": "Shared title"})

    assert response.status_code == 201
