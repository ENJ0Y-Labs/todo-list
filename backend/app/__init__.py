import os
from pathlib import Path

from cachelib import FileSystemCache
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
from werkzeug.exceptions import HTTPException

from .errors import ApiError
from .extensions import db
from .routes.auth import auth_bp
from .routes.tasks import tasks_bp

load_dotenv()

session_ext = Session()


def create_app(test_config=None):
    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")
    database_url = os.getenv("DATABASE_URL")

    if not test_config and not secret_key:
        raise RuntimeError("SECRET_KEY must be set.")
    if not test_config and not database_url:
        raise RuntimeError("DATABASE_URL must be set.")

    session_dir = Path(
        os.getenv(
            "SESSION_FILE_DIR",
            Path(__file__).resolve().parent.parent / ".flask_session",
        )
    )
    session_dir.mkdir(parents=True, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE="cachelib",
        SESSION_CACHELIB=FileSystemCache(str(session_dir)),
        SESSION_PERMANENT=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=os.getenv("SESSION_COOKIE_SAMESITE", "Lax"),
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    session_ext.init_app(app)

    allowed_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174").split(",")
        if origin.strip()
    ]
    CORS(app, origins=allowed_origins, supports_credentials=True)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({
            "error": {
                "code": error.code,
                "message": error.message,
            }
        }), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({
            "error": {
                "code": "HTTP_ERROR",
                "message": error.description,
            }
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled application error", exc_info=error)
        return jsonify({
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
            }
        }), 500

    return app
