"""Business logic for registration and authentication."""

from __future__ import annotations

import uuid
from typing import Dict, Tuple

from pymongo.errors import DuplicateKeyError

from auth.config import Settings
from auth.db import get_user_collection
from auth.exceptions import DuplicateEmailError, InvalidCredentialsError, UserNotFoundError
from auth.models import User
from auth.security import generate_jwt, hash_password, verify_password


def register_user(
    email: str,
    password: str,
    role: str,
    settings: Settings,
) -> Tuple[Dict[str, str], str]:
    """Create a new user and return their public data plus JWT."""
    normalized_email = email.strip().lower()
    user = User(
        user_id=str(uuid.uuid4()),
        email=normalized_email,
        password_hash=hash_password(password),
        role=role.strip(),
    )

    collection = get_user_collection(settings)
    try:
        collection.insert_one(user.to_document())
    except DuplicateKeyError:
        raise DuplicateEmailError(normalized_email) from None

    token = generate_jwt(
        {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role,
        }
    )

    return user.to_public_dict(), token


def authenticate_user(
    email: str,
    password: str,
    settings: Settings,
) -> Tuple[Dict[str, str], str]:
    """Validate credentials and return user data plus JWT."""
    normalized_email = email.strip().lower()
    collection = get_user_collection(settings)

    doc = collection.find_one({"email": normalized_email})
    if not doc:
        raise UserNotFoundError(normalized_email)

    user = User.from_document(doc)
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    token = generate_jwt(
        {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role,
        }
    )

    return user.to_public_dict(), token
