"""HTTP routes exposing the auth service."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict

from flask import Blueprint, current_app, g, jsonify, request

from auth.config import Settings
from auth.security import require_auth
from auth.services import authenticate_user, register_user
from auth.validation import validate_payload

bp = Blueprint("auth", __name__)


def _settings() -> Settings:
    return current_app.config["AUTH_SETTINGS"]


@bp.get("/healthz")
def health_check():
    return jsonify({"status": "ok"}), HTTPStatus.OK


@bp.post("/register")
def register_route():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    errors = validate_payload(["email", "password", "role", "organization_id"], payload)
    if errors:
        return jsonify({"error": "Invalid payload.", "details": errors}), HTTPStatus.BAD_REQUEST

    user, token = register_user(
        email=payload["email"],
        password=payload["password"],
        role=payload["role"],
        organization_id=payload["organization_id"],
        settings=_settings(),
    )

    return (
        jsonify(
            {
                "message": "User registered.",
                "user": user,
                "token": token,
            }
        ),
        HTTPStatus.CREATED,
    )


@bp.post("/login")
def login_route():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    errors = validate_payload(["email", "password"], payload)
    if errors:
        return jsonify({"error": "Invalid payload.", "details": errors}), HTTPStatus.BAD_REQUEST

    user, token = authenticate_user(
        email=payload["email"],
        password=payload["password"],
        settings=_settings(),
    )

    return (
        jsonify(
            {
                "message": "Login successful.",
                "user": user,
                "token": token,
            }
        ),
        HTTPStatus.OK,
    )


@bp.get("/me")
@require_auth
def current_user_route():
    claims = g.current_user
    return (
        jsonify(
            {
                "user": {
                    "user_id": claims["sub"],
                    "email": claims["email"],
                    "role": claims["role"],
                    "expires_at": claims["exp"],
                }
            }
        ),
        HTTPStatus.OK,
    )
