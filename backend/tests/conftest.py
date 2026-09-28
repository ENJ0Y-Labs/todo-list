import os
from pathlib import Path

import pytest
from cachelib import FileSystemCache

from app import create_app
from app.extensions import db


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture()
def app(tmp_path):
    if not TEST_DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL must be set to run PostgreSQL integration tests.")

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
            "SESSION_TYPE": "cachelib",
            "SESSION_CACHELIB": FileSystemCache(str(tmp_path / "sessions")),
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_SAMESITE": "Lax",
        }
    )

    migration_path = Path(__file__).resolve().parents[1] / "migrations" / "001_initial_schema.sql"
    migration_sql = migration_path.read_text(encoding="utf-8")

    with app.app_context():
        db.drop_all()
        db.session.connection().exec_driver_sql(migration_sql)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
