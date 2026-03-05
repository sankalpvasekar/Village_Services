from __future__ import annotations

import os
from typing import Optional

from django.conf import settings
from pymongo import MongoClient
from pymongo.database import Database

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    """
    Returns a singleton MongoClient using settings or environment variables.

    Priority:
    - settings.MONGODB_URI if present
    - env MONGODB_URI
    - fallback to mongodb://127.0.0.1:27017
    """
    global _client
    if _client is not None:
        return _client

    uri = getattr(settings, "MONGODB_URI", None) or os.getenv(
        "MONGODB_URI", "mongodb://127.0.0.1:27017"
    )

    # Safe defaults; tune as needed
    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> Database:
    """
    Returns a Database object for the configured DB name.

    Priority for DB name:
    - settings.MONGODB_DB_NAME if present
    - env MONGODB_DB_NAME
    - fallback to 'freelancer_db'
    """
    global _db
    if _db is not None:
        return _db

    db_name = getattr(settings, "MONGODB_DB_NAME", None) or os.getenv(
        "MONGODB_DB_NAME", "freelancer_db"
    )
    _db = get_client()[db_name]
    return _db


def close_client() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None
