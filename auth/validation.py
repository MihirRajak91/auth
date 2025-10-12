"""Helpers for validating incoming request payloads."""

from __future__ import annotations

from typing import Dict, List


def validate_payload(expected_fields: List[str], payload: Dict[str, object]) -> Dict[str, str]:
    """Ensure payload contains required non-empty string fields."""
    errors: Dict[str, str] = {}
    for field in expected_fields:
        value = payload.get(field, "")
        if not isinstance(value, str) or not value.strip():
            errors[field] = "This field is required."
    return errors
