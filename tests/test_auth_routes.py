from __future__ import annotations

import copy
from typing import Any, Dict

import pytest
from pymongo.errors import DuplicateKeyError

from auth import create_app


class FakeCollection:
    """Minimal in-memory collection that mimics the parts of pymongo we rely on."""

    def __init__(self) -> None:
        self._docs: Dict[str, Dict[str, Any]] = {}

    def create_index(self, *_args: Any, **_kwargs: Any) -> None:
        # Unique index enforcement is handled manually in insert_one.
        return None

    def insert_one(self, document: Dict[str, Any]) -> None:
        email = document["email"]
        if email in self._docs:
            raise DuplicateKeyError(f"Duplicate key error collection: {email}")
        # Store a defensive copy so later mutations won't leak into the "database".
        self._docs[email] = copy.deepcopy(document)

    def find_one(self, query: Dict[str, Any]) -> Dict[str, Any] | None:
        email = query.get("email")
        if email is None:
            return None
        doc = self._docs.get(email)
        return copy.deepcopy(doc) if doc is not None else None


@pytest.fixture()
def app(monkeypatch: pytest.MonkeyPatch):
    fake_collection = FakeCollection()

    def _fake_get_user_collection(_settings):
        return fake_collection

    monkeypatch.setattr("auth.services.get_user_collection", _fake_get_user_collection, raising=True)

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_register_creates_user_and_returns_token(client):
    payload = {
        "email": "agent@example.com",
        "password": "s3cret",
        "role": "agent",
        "organization_id": "org-123",
    }

    response = client.post("/register", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "User registered."
    assert body["user"]["email"] == payload["email"]
    assert body["user"]["role"] == payload["role"]
    assert "token" in body and isinstance(body["token"], str) and body["token"]


def test_register_duplicate_email_returns_conflict(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password1",
        "role": "admin",
        "organization_id": "org-456",
    }

    first = client.post("/register", json=payload)
    assert first.status_code == 201

    second = client.post("/register", json=payload)
    assert second.status_code == 409
    body = second.get_json()
    assert "already exists" in body["error"]


def test_login_requires_valid_credentials(client):
    payload = {
        "email": "login@example.com",
        "password": "hunter2",
        "role": "agent",
        "organization_id": "org-789",
    }
    client.post("/register", json=payload)

    bad_login = client.post("/login", json={"email": payload["email"], "password": "wrong"})
    assert bad_login.status_code == 401

    good_login = client.post(
        "/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert good_login.status_code == 200
    body = good_login.get_json()
    assert body["user"]["email"] == payload["email"]
    assert body["token"]


def test_me_requires_bearer_token(client):
    payload = {
        "email": "me@example.com",
        "password": "pass1234",
        "role": "agent",
        "organization_id": "org-999",
    }
    register_response = client.post("/register", json=payload)
    token = register_response.get_json()["token"]

    unauthenticated = client.get("/me")
    assert unauthenticated.status_code == 401

    authenticated = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert authenticated.status_code == 200
    body = authenticated.get_json()
    assert body["user"]["email"] == payload["email"]
    assert body["user"]["role"] == payload["role"]
