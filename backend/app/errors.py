"""Consistent JSON API errors."""

from flask import jsonify


class APIError(Exception):
    def __init__(self, status_code, code, message):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({
            "error": {
                "code": error.code,
                "message": error.message,
            }
        }), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Resource not found",
            }
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify({
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": "Method not allowed",
            }
        }), 405
