"""Auth package exposing Flask app factory."""

from __future__ import annotations

from flask import Flask

from .config import Settings, load_settings
from .error_handlers import register_error_handlers
from .routes import bp as auth_bp


def create_app(settings: Settings | None = None) -> Flask:
    """Create a Flask app instance configured with auth routes."""
    app = Flask(__name__)

    app.config["AUTH_SETTINGS"] = settings or load_settings()

    register_error_handlers(app)
    app.register_blueprint(auth_bp)

    return app
