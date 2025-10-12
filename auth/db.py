"""Database utilities for MongoDB access."""

from __future__ import annotations

from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from .config import Settings

_mongo_client: Optional[MongoClient] = None
_user_collection: Optional[Collection] = None


def get_mongo_client(settings: Settings) -> MongoClient:
    """Return a cached `MongoClient` instance."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.mongodb_uri)
    return _mongo_client


def get_user_collection(settings: Settings) -> Collection:
    """Return the users collection, ensuring a unique email index."""
    global _user_collection
    if _user_collection is None:
        client = get_mongo_client(settings)
        _user_collection = client[settings.db_name][settings.user_collection]
        _user_collection.create_index("email", unique=True)
    return _user_collection
