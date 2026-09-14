"""Seeds a fixed set of mock users on startup, for the "log in as" flow.

There is no password/auth provider in this assignment's scope; the frontend
lets the user pick one of these seeded identities and sends it as the
X-User-Id header on every subsequent request.
"""
from __future__ import annotations

from sqlmodel import Session, select

from .db_models import UserRow, engine

SEED_USERS = [
    {"id": "u-ada", "name": "Ada Lovelace", "email": "ada@example.com"},
    {"id": "u-alan", "name": "Alan Turing", "email": "alan@example.com"},
    {"id": "u-grace", "name": "Grace Hopper", "email": "grace@example.com"},
    {"id": "u-linus", "name": "Linus Torvalds", "email": "linus@example.com"},
]


def seed_users() -> None:
    with Session(engine) as session:
        for user in SEED_USERS:
            existing = session.get(UserRow, user["id"])
            if existing is None:
                session.add(UserRow(**user))
        session.commit()
