"""Shared pytest fixtures.

Uses a dedicated temporary SQLite file for the whole test session so
tests never touch the real dev database (backend/data/app.db). The
DATABASE_URL environment variable must be set *before* `src.infrastructure
.db_models` is first imported, since the module reads it at import time
to create the SQLAlchemy engine.
"""
from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(scope="session", autouse=True)
def _use_temp_database() -> None:
    tmp_dir = tempfile.mkdtemp(prefix="docs-backend-tests-")
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_dir}/test.db"


@pytest.fixture(scope="session")
def client(_use_temp_database):
    from fastapi.testclient import TestClient

    from src.main import app

    with TestClient(app) as test_client:
        yield test_client


# Seeded user ids, matching backend/src/infrastructure/seed.py
ADA = "u-ada"
ALAN = "u-alan"
GRACE = "u-grace"
LINUS = "u-linus"


def auth_headers(user_id: str) -> dict:
    return {"X-User-Id": user_id}
