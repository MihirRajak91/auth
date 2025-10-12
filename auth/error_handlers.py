"""Common error handlers registered on the Flask app."""

from __future__ import annotations

from flask import Flask, jsonify
from pymongo.errors import ServerSelectionTimeoutError
from werkzeug.exceptions import HTTPException

from auth import exceptions as exc


def register_error_handlers(app: Flask) -> None:
    """Attach HTTP and domain-specific error handlers."""

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        response = error.get_response()
        response.data = jsonify({"error": error.description}).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(ServerSelectionTimeoutError)
    def handle_db_timeout(_: ServerSelectionTimeoutError):
        return jsonify({"error": "Could not reach MongoDB. Check configuration."}), 503

    @app.errorhandler(exc.DuplicateEmailError)
    def handle_duplicate_email(error: exc.DuplicateEmailError):
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(exc.InvalidCredentialsError)
    def handle_invalid_credentials(error: exc.InvalidCredentialsError):
        return jsonify({"error": str(error)}), 401

    @app.errorhandler(exc.UserNotFoundError)
    def handle_user_not_found(error: exc.UserNotFoundError):
        return jsonify({"error": str(error)}), 404
