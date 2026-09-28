from datetime import datetime, timedelta, timezone


def register(client, email="test@example.com"):
    return client.post("/api/auth/register", json={
        "email": email,
        "password": "strong-password",
        "username": "tester",
        "fullname": "Test User",
    })


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_register_creates_session(client):
    response = register(client)

    assert response.status_code == 201
    assert response.get_json()["user"]["email"] == "test@example.com"

    me = client.get("/api/auth/me")
    assert me.status_code == 200


def test_duplicate_email_is_rejected(client):
    assert register(client).status_code == 201
    response = register(client, "TEST@example.com")

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_task_requires_authentication(client):
    response = client.get("/api/tasks")
    assert response.status_code == 401


def test_task_lifecycle(client):
    register(client)

    due_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    response = client.post("/api/tasks", json={
        "title": "Study Flask",
        "description": "Review API contracts",
        "due_at": due_at,
        "category": "school",
    })

    assert response.status_code == 201
    task = response.get_json()
    task_id = task["id"]
    assert task["completed"] is False

    response = client.patch(f"/api/tasks/{task_id}/complete", json={
        "completed": True,
    })
    assert response.status_code == 200
    assert response.get_json()["completed"] is True

    response = client.patch(f"/api/tasks/{task_id}", json={
        "title": "Study Flask API",
    })
    assert response.status_code == 200
    assert response.get_json()["title"] == "Study Flask API"

    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204

    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404


def test_past_due_date_is_rejected(client):
    register(client)

    response = client.post("/api/tasks", json={
        "title": "Past task",
        "due_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    })

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"
