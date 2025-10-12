"""Security helpers for password hashing and JWT management."""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, TypeVar

import bcrypt
import jwt
from flask import current_app, g, jsonify, request
from jwt import ExpiredSignatureError, InvalidTokenError

from auth.config import Settings

ViewFunc = TypeVar("ViewFunc", bound=Callable[..., Any])


def _get_settings() -> Settings:
    return current_app.config["AUTH_SETTINGS"]


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the provided password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Check whether the provided password matches the stored hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_jwt(claims: Dict[str, Any]) -> str:
    """Create a signed JWT for the given claims."""
    settings = _get_settings()
    now = datetime.utcnow()
    payload = {
        **claims,
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_exp_seconds),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_jwt(token: str) -> Dict[str, Any]:
    """Decode a JWT and return its claims."""
    settings = _get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )


def require_auth(fn: ViewFunc) -> ViewFunc:
    """Decorator to enforce Bearer token authentication."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"error": "Authorization header missing or malformed."}),
                401,
            )

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return (
                jsonify({"error": "Authorization header missing or malformed."}),
                401,
            )

        try:
            claims = decode_jwt(token)
        except ExpiredSignatureError:
            return jsonify({"error": "Token has expired."}), 401
        except InvalidTokenError:
            return jsonify({"error": "Token is invalid."}), 401

        g.current_user = claims
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
