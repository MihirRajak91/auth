"""Configuration helpers for the auth service."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    db_name: str
    user_collection: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_exp_seconds: int


def load_settings() -> Settings:
    """Load settings from environment variables with sane defaults."""
    return Settings(
        mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
        db_name=os.getenv("MONGODB_DB", "fiddle_auth"),
        user_collection=os.getenv("MONGODB_USER_COLLECTION", "users"),
        jwt_secret=os.getenv("JWT_SECRET", "change-me-in-production"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_exp_seconds=int(os.getenv("JWT_EXP_SECONDS", "3600")),
    )
