from __future__ import annotations

import os
from typing import Generator

import pytest
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from auth import create_app
from auth.config import Settings
from auth import db as db_module


@pytest.fixture(scope="module")
def mongo_settings() -> Generator[Settings, None, None]:
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = "auth_integration_tests"
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=1000)

    try:
        client.admin.command("ping")
    except ServerSelectionTimeoutError:
        pytest.skip("MongoDB is not reachable at the configured URI.")

    # Ensure the test database starts empty.
    client.drop_database(db_name)

    settings = Settings(
        mongodb_uri=mongodb_uri,
        db_name=db_name,
        user_collection="users",
        jwt_secret="integration-secret",
        jwt_algorithm="HS256",
        jwt_exp_seconds=3600,
    )

    yield settings

    client.drop_database(db_name)
    client.close()


@pytest.fixture()
def client(mongo_settings: Settings):
    # Reset cached connections so the app picks up our test settings.
    db_module._mongo_client = None
    db_module._user_collection = None

    app = create_app(settings=mongo_settings)
    app.config["TESTING"] = True
    test_client = app.test_client()
    yield test_client

    # Clear cached handles to avoid cross-test leakage.
    db_module._mongo_client = None
    db_module._user_collection = None


def test_register_login_flow_uses_real_mongo(client):
    register_payload = {
        "email": "integration@example.com",
        "password": "very-secret",
        "role": "agent",
        "organization_id": "integration-org",
    }

    register_resp = client.post("/register", json=register_payload)
    assert register_resp.status_code == 201
    register_body = register_resp.get_json()
    assert register_body["user"]["email"] == register_payload["email"]
    assert register_body["token"]

    login_resp = client.post(
        "/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_resp.status_code == 200
    login_body = login_resp.get_json()
    assert login_body["user"]["organization_id"] == register_payload["organization_id"]
    assert login_body["token"]

    me_resp = client.get("/me", headers={"Authorization": f"Bearer {login_body['token']}"})
    assert me_resp.status_code == 200
    me_body = me_resp.get_json()
    assert me_body["user"]["email"] == register_payload["email"]
