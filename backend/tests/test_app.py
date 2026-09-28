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
