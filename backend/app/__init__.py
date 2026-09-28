"""Flask application factory."""

import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .errors import register_error_handlers
from .extensions import db, server_session
from .auth import auth_bp
from .tasks import tasks_bp

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://user:password@localhost:5432/todo",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE=os.getenv("SESSION_TYPE", "filesystem"),
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=os.getenv("SESSION_COOKIE_SAMESITE", "Lax"),
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    server_session.init_app(app)
    CORS(
        app,
        supports_credentials=True,
        origins=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
    )
    register_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
