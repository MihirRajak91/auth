from __future__ import annotations

import base64
import json

import pytest
from jwt import InvalidTokenError

from auth import create_app
from auth.config import Settings
from auth.security import decode_jwt, generate_jwt


@pytest.fixture()
def app_context():
    settings = Settings(
        mongodb_uri="mongodb://unused:27017/",
        db_name="unused",
        user_collection="users",
        jwt_secret="unit-test-secret",
        jwt_algorithm="HS256",
        jwt_exp_seconds=3600,
    )
    app = create_app(settings=settings)
    with app.app_context():
        yield


def _tamper_token(token: str) -> str:
    """Flip one bit of payload to invalidate the signature."""
    header_b64, payload_b64, signature_b64 = token.split(".")
    payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
    payload = json.loads(payload_bytes)
    payload["email"] = "hacker@example.com"
    tampered_payload = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
    return ".".join([header_b64, tampered_payload, signature_b64])


def test_generate_and_decode_jwt_round_trip(app_context):
    claims = {"sub": "user-123", "email": "agent@example.com", "role": "agent"}
    token = generate_jwt(claims)

    decoded = decode_jwt(token)

    for key, value in claims.items():
        assert decoded[key] == value
    assert "iat" in decoded and "exp" in decoded


def test_decode_jwt_rejects_tampered_token(app_context):
    claims = {"sub": "user-999", "email": "victim@example.com", "role": "agent"}
    token = generate_jwt(claims)
    tampered = _tamper_token(token)

    with pytest.raises(InvalidTokenError):
        decode_jwt(tampered)
