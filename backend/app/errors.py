from flask import jsonify


class ApiError(Exception):
    def __init__(self, code, message, status_code):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def error_response(code, message, status_code):
    return jsonify({"error": {"code": code, "message": message}}), status_code
