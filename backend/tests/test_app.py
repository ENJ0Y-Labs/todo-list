from cachelib import FileSystemCache

from app import create_app


def test_create_app_can_be_called_twice(tmp_path):
    first = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_TYPE": "cachelib",
            "SESSION_CACHELIB": FileSystemCache(str(tmp_path / "first")),
        }
    )
    second = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_TYPE": "cachelib",
            "SESSION_CACHELIB": FileSystemCache(str(tmp_path / "second")),
        }
    )

    assert first is not second


def test_unexpected_errors_use_json_contract(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_TYPE": "cachelib",
            "SESSION_CACHELIB": FileSystemCache(str(tmp_path / "sessions")),
        }
    )

    @app.get("/api/test-error")
    def test_error():
        raise RuntimeError("private implementation detail")

    response = app.test_client().get("/api/test-error")

    assert response.status_code == 500
    assert response.content_type.startswith("application/json")
    assert response.json == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
        }
    }


def test_cors_allows_vite_5174(monkeypatch, tmp_path):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174")
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_TYPE": "cachelib",
            "SESSION_CACHELIB": FileSystemCache(str(tmp_path / "sessions")),
        }
    )

    response = app.test_client().options(
        "/api/auth/register",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5174"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
