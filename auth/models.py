"""Domain models used by the auth service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class User:
    user_id: str
    email: str
    password_hash: str
    role: str

    @classmethod
    def from_document(cls, doc: Dict[str, Any]) -> "User":
        return cls(
            user_id=doc["user_id"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            role=doc["role"],
        )

    def to_document(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
        }

    def to_public_dict(self) -> Dict[str, str]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role,
        }
